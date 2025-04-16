"""
Implementación de DeepSeek como proveedor de IA.
"""
import json
from typing import Dict, Any
from openai import OpenAI
from bson.regex import Regex

from .base import AIProvider
from .serpapi_provider import SerpAPIProvider
from .prompts import get_news_summary_prompt, get_keyword_extraction_prompt, get_current_date_formatted
from .prompts import get_fallback_content, get_email_template
from ..database import db


class DeepSeekProvider(AIProvider):
    """
    Implementación del proveedor de IA DeepSeek.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA DeepSeek.
        
        Args:
            api_key: La clave API de DeepSeek
            kwargs: Parámetros adicionales como modelo y clave API de búsqueda
        """
        self.api_key = api_key
        self.serpapi_key = kwargs.get("serpapi_key", "")
        self.model = kwargs.get("model", "deepseek-chat")
        self.search_provider = None
        
        if self.serpapi_key:
            self.search_provider = SerpAPIProvider(self.serpapi_key)
        
        # Inicializar cliente de DeepSeek
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com",
        )
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de DeepSeek.
        
        Args:
            prompt: El prompt para generar contenido
            kwargs: Parámetros adicionales como temperatura
            
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            return response.choices[0].message.content or ""
        except Exception as e:
            print(f"Error generando contenido con DeepSeek: {str(e)}")
            return f"Error: {str(e)}"
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando SerpAPI y procesa los resultados con DeepSeek.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados procesados de la búsqueda
        """
        if not self.search_provider:
            return {"error": "No se ha configurado un proveedor de búsqueda", "success": False}
        
        try:
            # Primero obtenemos la keyword mediante DeepSeek
            system_prompt = get_keyword_extraction_prompt()
            
            keyword_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extraer la keyword del JSON
            content_str = keyword_response.choices[0].message.content or "{}"
            keyword_json = json.loads(content_str)
            keyword = keyword_json.get("keyword", query)
            
            # Realizar búsqueda con SerpAPI
            search_results = self.search_provider.search(keyword)
            
            # Verificar si hay resultados y si contiene answer_box
            if "error" in search_results:
                return {"error": search_results["error"], "success": False}
            
            answer_box = search_results.get("answer_box", {})
            organic_results = search_results.get("organic_results", [])
            
            # Preparar contenido para procesar con DeepSeek
            content_to_process = ""
            
            if answer_box:
                content_to_process += f"ANSWER BOX: {json.dumps(answer_box, indent=2)}\n\n"
            
            if organic_results and len(organic_results) > 0:
                content_to_process += "TOP RESULTS:\n"
                for idx, result in enumerate(organic_results[:5]):  # Tomamos los primeros 5 resultados
                    content_to_process += f"{idx+1}. {result.get('title', 'No Title')}: {result.get('snippet', 'No Snippet')}\n"
            
            if not content_to_process:
                return {"error": "No se encontraron resultados relevantes", "success": False}
            
            # Procesar los resultados con DeepSeek
            system_content = f"Answer the question from user with the provided search information: {content_to_process}"
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": query}
                ]
            )
            
            return {
                "content": final_response.choices[0].message.content,
                "success": True,
                "search_results": search_results
            }
            
        except Exception as e:
            print(f"Error en búsqueda web con DeepSeek: {str(e)}")
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
            # Realizar la búsqueda web
            search_result = self.search_web(query)
            
            if not search_result.get("success", False):
                # Usar la función centralizada en lugar del método local
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
            print(f"Error al generar contenido con DeepSeek: {str(e)}")
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
        
        # Usar la función centralizada para generar el contenido de respaldo
        return get_fallback_content(username, language)