"""
Definición de prompts globales para los servicios de IA.
Este archivo centraliza todos los prompts utilizados por los diferentes proveedores de IA
para garantizar consistencia en los resultados.
"""
from datetime import datetime

# Formato común para fechas según el idioma
DATE_FORMAT = {
    "es": "%d de %B de %Y",
    "en": "%B %d, %Y"
}

def get_current_date_formatted(language="es"):
    """
    Obtiene la fecha actual formateada según el idioma
    
    Args:
        language: Código de idioma ('es' o 'en')
        
    Returns:
        str: Fecha formateada según el idioma
    """
    language = language.lower()
    if language not in DATE_FORMAT:
        language = "es"  # Idioma por defecto
    
    return datetime.now().strftime(DATE_FORMAT[language])

# Plantilla para emails de resumen
def get_email_template(username, content, language="es"):
    """
    Genera una plantilla de email con el contenido proporcionado.
    
    Args:
        username: Nombre de usuario (extraído del email)
        content: Contenido principal del email
        language: Idioma del email ('es' o 'en')
        current_date: Fecha formateada (opcional, si no se proporciona se genera)
        
    Returns:
        str: Email formateado
    """
    
    if language.lower() == "en":
        return f"""Hello {username},
{content}
"""
    else:  # Español por defecto
        return f"""Hola {username},

{content}
"""

def get_welcome_email_template(username, language="es"):
    """
    Genera una plantilla de email de bienvenida estática y ligera.
    
    Args:
        username: Nombre de usuario (extraído del email)
        language: Idioma del email ('es' o 'en')
        
    Returns:
        str: Email de bienvenida formateado
    """
    current_date = get_current_date_formatted(language)
    
    if language.lower() == "en":
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            <h2 style="color: #3B82F6;">Welcome to UpdateMe!</h2>
            
            <p>Hello {username},</p>
            
            <p>Thank you for subscribing to UpdateMe! We're thrilled to have you join our community of technology and AI enthusiasts.</p>
            
            <p>What you can expect from us:</p>
            <ul>
                <li>Weekly summaries of the most important tech and AI news</li>
                <li>Curated content from reliable sources</li>
                <li>Clear and concise information to keep you up-to-date</li>
            </ul>
            
            <p><strong>Your first complete weekly summary will arrive in your inbox shortly.</strong></p>
            
            <p>If you have any questions or feedback, feel free to reply to this email.</p>
            
            <p>Best regards,<br>
            The UpdateMe Team</p>
            
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                Date sent: {current_date}<br>
                This email was automatically generated. Please do not reply to this message.<br>
                If you wish to unsubscribe, click the unsubscribe link on our website.
            </p>
        </div>
        """
    else:  # Español por defecto
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
            <h2 style="color: #3B82F6;">¡Bienvenido a UpdateMe!</h2>
            
            <p>Hola {username},</p>
            
            <p>¡Gracias por suscribirte a UpdateMe! Estamos encantados de que te unas a nuestra comunidad de entusiastas de la tecnología e IA.</p>
            
            <p>Lo que puedes esperar de nosotros:</p>
            <ul>
                <li>Resúmenes semanales de las noticias más importantes de tecnología e IA</li>
                <li>Contenido seleccionado de fuentes confiables</li>
                <li>Información clara y concisa para mantenerte al día</li>
            </ul>
            
            <p><strong>Tu primer resumen semanal completo llegará a tu bandeja de entrada en breve.</strong></p>
            
            <p>Si tienes alguna pregunta o comentario, no dudes en responder a este correo.</p>
            
            <p>Saludos cordiales,<br>
            El equipo de UpdateMe</p>
            
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 12px; color: #666;">
                Fecha de envío: {current_date}<br>
                Este correo ha sido generado automáticamente. No responda a este mensaje.<br>
                Si desea darse de baja, haga clic en el enlace de cancelación de suscripción en nuestro sitio web.
            </p>
        </div>
        """

# Prompt para la generación de resúmenes de noticias de tecnología e IA
def get_news_summary_prompt(language="es"):
    """
    Obtiene el prompt para la generación de resúmenes de noticias,
    incluyendo la fecha actual.
    
    Args:
        language: Idioma del prompt ('es' o 'en')
        
    Returns:
        str: Prompt para generar resumen de noticias
    """
    
    return f"""
    Eres un asistente especializado en crear boletines informativos profesionales.
    Tu tarea es generar un boletín que resuma las 5 noticias más importantes y relevantes
    sobre tecnología e inteligencia artificial de la última semana.
    
    Para cada noticia, incluye:
    1. Un título claro y conciso
    2. Un resumen de 2-3 oraciones que explique la noticia
    3. La fuente de la noticia (publicación reconocida)
    4. La fecha aproximada de publicación (dentro de la última semana)
    
    Las noticias deben estar ordenadas por relevancia e impacto global.
    Prioriza fuentes confiables como TechCrunch, Wired, MIT Technology Review, 
    The Verge, BBC Technology, CNN Tech, entre otras.
    
    Formatea tu respuesta como un correo electrónico profesional que incluya:
    - Las noticias numeradas claramente
    - Una breve conclusión
    
    Usa un tono profesional pero accesible. NO incluyas hiperenlaces en tu respuesta, 
    solo menciona las fuentes.
    
    Hazlo compatible con formato HTML para correos electrónicos.
    
    Aunque sea un mensaje profesional, no incluyas saludo ni despedida.
    
    IMPORTANTE: Genera el contenido en {language.upper()} ({"español" if language.lower() == "es" else "English"}).
    """

# Prompt para la búsqueda web simulada
def get_web_search_prompt(language="es"):
    """
    Obtiene el prompt para el procesamiento de resultados de búsqueda web.
    Este prompt se utiliza para dar formato a los resultados de búsqueda
    y no para realizar la búsqueda en sí.
    
    Args:
        language: Idioma del prompt ('es' o 'en')
        
    Returns:
        str: Prompt para procesamiento de resultados de búsqueda web
    """
    return f"""
    Combina y resume los resultados de búsqueda web a continuación para proporcionar
    una respuesta completa y coherente a la consulta del usuario.
    
    Debes:
    1. Extraer información relevante y actualizada de los resultados proporcionados
    2. Citar las fuentes correctamente cuando menciones información específica
    3. Asegurarte de que la información proporcionada sea precisa y esté respaldada por los resultados
    4. Organizar la respuesta de manera lógica y coherente
    
    Utiliza un tono informativo y objetivo. Cuando corresponda, incluye fechas para mostrar
    la actualidad de la información.
    
    Si los resultados de la búsqueda no contienen información suficiente para responder
    a la consulta, indica claramente las limitaciones de la respuesta.
    
    IMPORTANTE: Genera el contenido en {language.upper()} ({"español" if language.lower() == "es" else "inglés"}).
    """

# Configuraciones predeterminadas para los servicios de búsqueda web
def get_default_search_configs():
    """
    Obtiene las configuraciones predeterminadas para los proveedores de búsqueda.
    
    Returns:
        dict: Configuraciones predeterminadas para cada proveedor de búsqueda
    """
    return {
        "tavily": {
            "max_results": 5,
            "topic": "news",
            "search_depth": "moderate",  # "basic", "moderate", o "comprehensive"
            "time_range": "week",        # "day", "week", "month", o "year"
            "include_raw_content": True,
            "include_domains": [],
            "exclude_domains": [],
            "days": 7,                # Número de días para buscar en el pasado
        },
        "serpapi": {
            "max_results": 5,
            "search_type": "news",       # "news", "web", "images", o "videos"
            "safe_search": "off",
            "time_range": "week",        # "day", "week", "month", o "year"
            "include_domains": [],
            "exclude_domains": []
        }
    }

# Prompt para extracción de palabras clave (usado por DeepSeek)
def get_keyword_extraction_prompt():
    """
    Obtiene el prompt para la extracción de palabras clave.
    Este prompt es independiente del idioma ya que es usado internamente
    para optimizar búsquedas.
    """
    return """
    Please parse the "keyword" from user's message to be used in a Google search and output them in JSON format. 
    Make the keyword concise, focused, and optimized for search engines.

    EXAMPLE INPUT: 
    What's the weather like in New York today?

    EXAMPLE JSON OUTPUT:
    {
        "keyword": "weather in New York"
    }
    """

# Prompt de fallback para cuando falla la generación con IA
def get_fallback_content(username, language="es"):
    """
    Genera un contenido de respaldo cuando falla la generación con IA.
    
    Args:
        username: Nombre de usuario (extraído del email)
        language: Idioma del contenido ('es' o 'en')
        
    Returns:
        str: Contenido de respaldo formateado
    """
    if language.lower() == "en":
        return f"""Hello {username},

Here is a summary of the most important tech news from the past week:

1. The new version of Python 3.13 has been released with significant performance improvements.
   Source: Python.org (April 15, 2025)

2. Microsoft announces important advances in its generative AI model that improves contextual understanding.
   Source: Microsoft Research Blog (April 14, 2025)

3. The European Union approves stricter regulations for data protection in mobile applications.
   Source: European Commission (April 12, 2025)

4. Apple introduces new battery technology with 40% longer life for its upcoming devices.
   Source: Apple Newsroom (April 13, 2025)

5. Google implements revolutionary changes to its search algorithm using advanced AI.
   Source: Google Blog (April 11, 2025)

Thank you for subscribing to UpdateMe!
"""
    else:  # Español por defecto
        return f"""Hola {username},

Aquí tienes un resumen de las noticias tecnológicas más importantes de la última semana:

1. La nueva versión de Python 3.13 ha sido lanzada con mejoras significativas en rendimiento.
   Fuente: Python.org (15 de abril de 2025)

2. Microsoft anuncia avances importantes en su modelo de IA generativa que mejora la comprensión contextual.
   Fuente: Microsoft Research Blog (14 de abril de 2025)

3. La Unión Europea aprueba una regulación más estricta para la protección de datos en aplicaciones móviles.
   Fuente: European Commission (12 de abril de 2025)

4. Apple presenta nueva tecnología de batería con un 40% más de duración para sus próximos dispositivos.
   Fuente: Apple Newsroom (13 de abril de 2025)

5. Google implementa cambios revolucionarios en su algoritmo de búsqueda utilizando IA avanzada.
   Fuente: Google Blog (11 de abril de 2025)
"""