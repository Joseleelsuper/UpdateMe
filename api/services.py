"""
Este archivo contiene funciones para interactuar con servicios externos como Resend (email) y APIs de IA.
"""
import os
import resend
from dotenv import load_dotenv
from typing import Dict, Optional
from datetime import datetime, timedelta
from .cache_manager import CacheManager
from .serviceAi.prompts import get_fallback_content

# Importar proveedores de IA
from .serviceAi.openai_provider import OpenAIProvider
from .serviceAi.deepseek_provider import DeepSeekProvider
from .serviceAi.groq_provider import GroqProvider
from .serviceAi.base import AIProvider
from .serviceAi.prompts import get_welcome_email_template, get_email_template
from .database import db

# Cargar variables de entorno si no se han cargado
load_dotenv()

# Configuración Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# Claves API para servicios de IA y búsqueda
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")

# Diccionario de proveedores disponibles
ai_providers: Dict[str, AIProvider] = {}

# Inicializar proveedores si las claves están disponibles
if OPENAI_API_KEY:
    ai_providers["openai"] = OpenAIProvider(OPENAI_API_KEY, model="gpt-4o-mini")

if DEEPSEEK_API_KEY:
    # Configurar DeepSeek para usar Tavily como proveedor de búsqueda por defecto
    # Si no está disponible Tavily, usar SerpAPI como respaldo
    if TAVILY_API_KEY:
        ai_providers["deepseek"] = DeepSeekProvider(
            DEEPSEEK_API_KEY, 
            tavily_key=TAVILY_API_KEY,
            search_provider="tavily"
        )
    elif SERPAPI_API_KEY:
        ai_providers["deepseek"] = DeepSeekProvider(
            DEEPSEEK_API_KEY, 
            serpapi_key=SERPAPI_API_KEY
        )

if GROQ_API_KEY:
    # Configurar Groq para usar Tavily como proveedor de búsqueda por defecto
    # Si no está disponible Tavily, usar SerpAPI como respaldo
    if TAVILY_API_KEY:
        ai_providers["groq"] = GroqProvider(
            GROQ_API_KEY, 
            model="llama3-70b-8192", 
            tavily_key=TAVILY_API_KEY,
            search_provider="tavily"
        )
    elif SERPAPI_API_KEY:
        ai_providers["groq"] = GroqProvider(
            GROQ_API_KEY, 
            model="llama3-70b-8192", 
            serpapi_key=SERPAPI_API_KEY
        )


def get_ai_provider(provider_name: str) -> Optional[AIProvider]:
    """
    Obtiene una instancia del proveedor de IA solicitado.
    
    Args:
        provider_name: Nombre del proveedor de IA
        
    Returns:
        Instancia del proveedor de IA o None si no está disponible
    """
    provider_name = provider_name.lower()
    return ai_providers.get(provider_name)


def send_email(to_email, subject, content):
    """
    Envía un correo electrónico usando Resend.
    
    Args:
        to_email: Dirección de correo del destinatario
        subject: Asunto del correo
        content: Contenido en texto plano del correo
        
    Returns:
        dict: Respuesta de la API de Resend
        
    Raises:
        Exception: Si hay algún error al enviar el correo
    """
    params: resend.Emails.SendParams = {
        "from": "UpdateMe <newsletter@updateme.dev>",
        "to": [to_email],
        "subject": subject,
        "html": content,
    }
    
    return resend.Emails.send(params)


def send_welcome_email(to_email):
    """
    Envía un correo electrónico de bienvenida ligero y estático sin generación de IA.
    
    Args:
        to_email: Dirección de correo del destinatario
        
    Returns:
        dict: Respuesta de la API de Resend
        
    Raises:
        Exception: Si hay algún error al enviar el correo
    """
    username = to_email.split("@")[0]
    
    # Obtener el idioma del usuario de la base de datos
    user_data = db.users.find_one({"email": to_email})
    language = user_data.get("language", "es") if user_data else "es"
    
    # Obtener plantilla de bienvenida (contenido estático)
    content = get_welcome_email_template(username, language)
    
    # Asunto según el idioma
    subject = "Welcome to UpdateMe!" if language == "en" else "¡Bienvenido a UpdateMe!"
    
    contact_params: resend.Contacts.CreateParams = {
        "email": to_email,
        "first_name": username,
        "unsubscribed": False,
        "audience_id": "d9811e04-dd4c-4843-8ae4-27d3ac0524e5",
    }

    resend.Contacts.create(contact_params)

    params: resend.Emails.SendParams = {
        "from": "UpdateMe <welcome@updateme.dev>",
        "to": [to_email],
        "subject": subject,
        "html": content,
    }

    return resend.Emails.send(params)


def generate_news_summary(email, provider=None):
    """
    Genera un resumen de noticias tecnológicas de la última semana usando IA.
    Utiliza el proveedor especificado por el usuario o el que se pase como parámetro.
    
    Args:
        email: Email del usuario (para personalizar el mensaje)
        provider: Proveedor de IA a utilizar (opcional, si no se especifica se usa el del usuario)
        
    Returns:
        str: Texto con el resumen de noticias
    """
    
    # Buscar al usuario en la base de datos para obtener su proveedor de IA preferido
    user_data = db.users.find_one({"email": email})
    
    # Extraer username e idioma para fallback
    username = email.split("@")[0]
    language = user_data.get("language", "es") if user_data else "es"
    
    # Si no se especifica un proveedor, usar el del usuario (o 'groq' por defecto)
    if not provider and user_data:
        provider = user_data.get("ai_provider", "groq")
    elif not provider:
        provider = "groq"  # Valor por defecto si no hay usuario ni proveedor especificado
    
    # Lista de proveedores a intentar, comenzando por el preferido del usuario
    providers_to_try = [provider]
    
    # Añadir el resto de proveedores disponibles a la lista
    for p in ai_providers:
        if p not in providers_to_try:
            providers_to_try.append(p)
    
    # Intentar con cada proveedor disponible
    for current_provider in providers_to_try:
        try:
            ai_provider = ai_providers.get(current_provider)
            if ai_provider:
                return ai_provider.generate_news_summary(email)
        except Exception as e:
            print(f"Error con proveedor {current_provider}: {str(e)}")
            continue
    
    # Si llegamos aquí, ningún proveedor funcionó
    # Buscar en la caché de días anteriores (hasta 2 días)
    
    # Obtener fechas de hoy, ayer y anteayer
    today = datetime.now()
    dates_to_check = [
        today.strftime("%Y-%m-%d"),
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        (today - timedelta(days=2)).strftime("%Y-%m-%d")
    ]
    
    # Primero intentar con el proveedor preferido del usuario
    for date in dates_to_check:
        cached_items = list(CacheManager.get_provider_cache_by_date(provider, date))
        if cached_items:
            print(f"Usando caché del {date} para proveedor {provider}")
            # Usar el primer resultado disponible
            return get_email_template(username, cached_items[0]["response"], language)
    
    # Si no hay caché del proveedor preferido, intentar con otros proveedores
    for current_provider in providers_to_try:
        if current_provider != provider:  # Evitamos comprobar de nuevo el proveedor preferido
            for date in dates_to_check:
                cached_items = list(CacheManager.get_provider_cache_by_date(current_provider, date))
                if cached_items:
                    print(f"Usando caché del {date} para proveedor {current_provider}")
                    return get_email_template(username, cached_items[0]["response"], language)
    
    # Si no hay resultados en caché, usar fallback
    return get_fallback_content(username, language)
