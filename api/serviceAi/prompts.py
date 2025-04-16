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
def get_email_template(username, content, language="es", current_date=None):
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
    if current_date is None:
        current_date = get_current_date_formatted(language)
    
    if language.lower() == "en":
        return f"""Hello {username},

{content}

Thank you for subscribing to UpdateMe. We will continue to keep you informed about the latest in technology and AI.

Best regards,
The UpdateMe Team

---
Date sent: {current_date}
This email was automatically generated. Please do not reply to this message.
If you wish to unsubscribe, click the unsubscribe link on our website.
"""
    else:  # Español por defecto
        return f"""Hola {username},

{content}

Gracias por suscribirte a UpdateMe. Seguiremos manteniéndote informado sobre las últimas novedades en tecnología e IA.

Atentamente,
El equipo de UpdateMe

---
Fecha de envío: {current_date}
Este correo ha sido generado automáticamente. No responda a este mensaje.
Si desea darse de baja, haga clic en el enlace de cancelación de suscripción en nuestro sitio web.
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
    current_date = get_current_date_formatted(language)
    
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
    
    La fecha actual es {current_date}. Hazlo compatible con formato HTML para correos electrónicos.
    
    Aunque sea un mensaje profesional, no incluyas saludo ni despedida.
    
    IMPORTANTE: Genera el contenido en {language.upper()} ({"español" if language.lower() == "es" else "inglés"}).
    """

# Prompt para la búsqueda web simulada
def get_web_search_prompt(language="es"):
    """
    Obtiene el prompt para simulación de búsqueda web.
    
    Args:
        language: Idioma del prompt ('es' o 'en')
        
    Returns:
        str: Prompt para simulación de búsqueda web
    """
    return f"""
    Actúa como un servicio de búsqueda web actualizado. El usuario te dará una consulta
    de búsqueda, y debes proporcionar información relevante y actualizada como si hubieras
    buscado en la web. Incluye:
    
    1. Información relevante y actualizada sobre el tema
    2. Datos de fuentes que podrían ser relevantes (menciona fuentes creíbles)
    3. Para temas de tecnología y noticias, asume la fecha actual
    
    No inventes enlaces pero sí menciona fuentes creíbles que podrían tener esta información.
    
    IMPORTANTE: Genera el contenido en {language.upper()} ({"español" if language.lower() == "es" else "inglés"}).
    """

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
    current_date = get_current_date_formatted(language)
    
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

Best regards,
The UpdateMe Team

---
Date sent: {current_date}
This email was automatically generated. Do not reply to this message.
If you wish to unsubscribe, click the unsubscribe link on our website.
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

¡Gracias por suscribirte a UpdateMe!

Atentamente,
El equipo de UpdateMe

---
Fecha de envío: {current_date}
Este correo ha sido generado automáticamente. No responda a este mensaje.
Si desea darse de baja, haga clic en el enlace de cancelación de suscripción en nuestro sitio web.
"""