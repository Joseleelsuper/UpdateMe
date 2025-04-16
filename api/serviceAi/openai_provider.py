"""
Implementación de OpenAI como proveedor de IA.
"""
import openai
from typing import Dict, Any
from bson.regex import Regex

from .base import AIProvider
from .prompts import get_news_summary_prompt, get_current_date_formatted, get_email_template, get_fallback_content
from ..database import db


class OpenAIProvider(AIProvider):
    """
    Implementación del proveedor de IA OpenAI.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA OpenAI.
        
        Args:
            api_key: La clave API de OpenAI
            kwargs: Parámetros adicionales como modelo
        """
        self.api_key = api_key
        openai.api_key = api_key
        self.model = kwargs.get("model", "gpt-4o-mini")
        
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de OpenAI.
        
        Args:
            prompt: El prompt para generar contenido
            kwargs: Parámetros adicionales como temperatura y system_content
            
        Returns:
            El contenido generado como string
        """
        try:
            temperature = kwargs.get("temperature", 0.7)
            system_content = kwargs.get("system_content", "")
            
            messages = []
            if system_content:
                messages.append({"role": "system", "content": system_content})
            
            messages.append({"role": "user", "content": prompt})
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"Error generando contenido con OpenAI: {str(e)}")
            return f"Error: {str(e)}"
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando las capacidades integradas de OpenAI.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados procesados de la búsqueda
        """
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": query}
                ],
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"}
                            },
                            "required": ["query"]
                        }
                    }
                }],
                tool_choice="auto"
            )
            
            return {"content": response.choices[0].message.content, "success": True}
        except Exception as e:
            print(f"Error en búsqueda web con OpenAI: {str(e)}")
            return {"error": str(e), "success": False}
    
    def generate_news_summary(self, email: str) -> str:
        """
        Genera un resumen de noticias personalizado para el usuario.
        
        Args:
            email: El email del usuario
            
        Returns:
            El resumen de noticias formateado como un email
        """
        # Extraer username y obtener el idioma del usuario desde la base de datos
        
        username = email.split("@")[0]
        
        # Buscar al usuario en la base de datos
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        language = user_data.get("language", "es") if user_data else "es"
        
        # Obtener la fecha actual para el saludo
        current_date = get_current_date_formatted(language)
        
        # Crear consulta para buscar noticias de tecnología e IA
        query = "Latest technology and AI news this week, top 5 most important news"
        
        try:
            # Realizar la búsqueda web y generación de contenido
            search_result = self.search_web(query)
            
            if not search_result.get("success", False):
                return get_fallback_content(username, language)
            
            # Procesar los resultados para generar un resumen bien formateado
            system_prompt = get_news_summary_prompt(language)
            
            news_content = self.generate_content(
                prompt=search_result.get("content", ""),
                system_content=system_prompt
            )
            
            # Formatear el email final con el contenido generado
            return get_email_template(username, news_content, language, current_date)
            
        except Exception as e:
            print(f"Error al generar contenido con OpenAI: {str(e)}")
            return get_fallback_content(username, language)
    
    def _generate_fallback_content(self, email: str) -> str:
        """
        Genera un contenido de respaldo cuando falla la generación con IA.
        
        Args:
            email: Email del usuario
            
        Returns:
            str: Contenido de respaldo
        """
        # Extraer username y obtener el idioma del usuario desde la base de datos
        
        username = email.split("@")[0]
        
        # Buscar al usuario en la base de datos
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        language = user_data.get("language", "es") if user_data else "es"
        
        return get_fallback_content(username, language)