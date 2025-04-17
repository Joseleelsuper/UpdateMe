"""
Este archivo contiene funciones para interactuar con servicios externos como Resend (email) y APIs de IA.
"""
import os
import resend
from dotenv import load_dotenv
from typing import Dict, Optional

# Importar proveedores de IA
from .serviceAi.openai_provider import OpenAIProvider
from .serviceAi.deepseek_provider import DeepSeekProvider
from .serviceAi.groq_provider import GroqProvider
from .serviceAi.base import AIProvider
from .serviceAi.prompts import get_welcome_email_template

# Cargar variables de entorno si no se han cargado
load_dotenv()

# Configuración Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

# Claves API para servicios de IA y búsqueda
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY", "")

# Diccionario de proveedores disponibles
ai_providers: Dict[str, AIProvider] = {}

# Inicializar proveedores si las claves están disponibles
if OPENAI_API_KEY:
    ai_providers["openai"] = OpenAIProvider(OPENAI_API_KEY, model="gpt-4o-mini")

if DEEPSEEK_API_KEY and SERPAPI_API_KEY:
    ai_providers["deepseek"] = DeepSeekProvider(DEEPSEEK_API_KEY, serpapi_key=SERPAPI_API_KEY)

if GROQ_API_KEY:
    # Pasar la clave de SerpAPI a Groq si está disponible
    ai_providers["groq"] = GroqProvider(GROQ_API_KEY, model="llama3-70b-8192", serpapi_key=SERPAPI_API_KEY)


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
        "from": "UpdateMe <onboarding@resend.dev>",
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
    
    # Obtener idioma del correo (podría obtenerse de la base de datos si está disponible)
    language = "es"  # Por defecto español
    
    # Obtener plantilla de bienvenida (contenido estático)
    content = get_welcome_email_template(username, language)
    
    params: resend.Emails.SendParams = {
        "from": "UpdateMe <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "¡Bienvenido a UpdateMe!",
        "html": content,
    }
    
    return resend.Emails.send(params)


def generate_news_summary(email, provider="groq"):
    """
    Genera un resumen de noticias tecnológicas de la última semana usando IA.
    Utiliza el proveedor especificado para generar el contenido.
    
    Args:
        email: Email del usuario (para personalizar el mensaje)
        provider: Proveedor de IA a utilizar ("openai", "deepseek", "groq", etc.)
        
    Returns:
        str: Texto con el resumen de noticias
    """
    # Obtener el proveedor solicitado
    ai_provider = get_ai_provider(provider)
    
    # Si el proveedor no está disponible, intentar con el primero disponible
    if not ai_provider and ai_providers:
        provider = next(iter(ai_providers))
        ai_provider = ai_providers[provider]
    
    # Si no hay proveedores disponibles, usar contenido de respaldo
    if not ai_provider:
        from .serviceAi.prompts import get_fallback_content
        username = email.split("@")[0]
        return get_fallback_content(username)
    
    # Generar resumen de noticias usando el proveedor
    return ai_provider.generate_news_summary(email)
