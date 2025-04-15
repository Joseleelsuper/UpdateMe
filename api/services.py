"""
Este archivo contiene funciones para interactuar con servicios externos como Resend (email) y APIs de IA.
"""
import os
import resend
from dotenv import load_dotenv

# Cargar variables de entorno si no se han cargado
load_dotenv()

# Configuración Resend
resend.api_key = os.environ.get("RESEND_API_KEY")

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
        "text": content,
    }
    
    return resend.Emails.send(params)

def generate_news_summary(email, provider="groq"):
    """
    Genera un resumen de noticias tecnológicas de la última semana usando IA.
    Por defecto usa Groq, pero se puede cambiar el proveedor fácilmente.
    
    Args:
        email: Email del usuario (para personalizar el mensaje)
        provider: Proveedor de IA a utilizar (groq, openai, etc.)
        
    Returns:
        str: Texto con el resumen de noticias
    """
    # TODO: Implementar integraciones reales con Groq, OpenAI, etc.
    # Por ahora, devuelve un texto simulado
    return f"""Hola {email},

Aquí tienes un resumen de las noticias tecnológicas más importantes de la última semana:

- Noticia 1: La nueva versión de Python 3.13 ha sido lanzada con mejoras significativas en rendimiento.
- Noticia 2: Microsoft anuncia avances importantes en su modelo de IA generativa.
- Noticia 3: La UE aprueba una regulación más estricta para la protección de datos en aplicaciones móviles.

¡Gracias por suscribirte a UpdateMe!

Atentamente,
El equipo de UpdateMe"""