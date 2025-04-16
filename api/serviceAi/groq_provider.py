"""
Implementación de Groq como proveedor de IA.
"""
import json
from typing import Dict, Any
from openai import OpenAI
from bson.regex import Regex

from .base import AIProvider
from .serpapi_provider import SerpAPIProvider
from .prompts import get_news_summary_prompt, get_web_search_prompt, get_keyword_extraction_prompt
from .prompts import get_current_date_formatted, get_fallback_content, get_email_template
from ..database import db

class GroqProvider(AIProvider):
    """
    Implementación del proveedor de IA Groq.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA Groq.
        
        Args:
            api_key: La clave API de Groq
            kwargs: Parámetros adicionales como modelo y clave API de búsqueda
        """
        self.api_key = api_key
        self.serpapi_key = kwargs.get("serpapi_key", "")
        self.model = kwargs.get("model", "llama3-70b-8192")
        self.search_provider = None
        
        if self.serpapi_key:
            self.search_provider = SerpAPIProvider(self.serpapi_key)
        
        # Inicializar cliente de Groq (usa la misma interfaz que OpenAI)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido utilizando la API de Groq.
        
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
            
            content = response.choices[0].message.content
            return content if content is not None else ""
        except Exception as e:
            print(f"Error generando contenido con Groq: {str(e)}")
            return f"Error: {str(e)}"
    
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web utilizando SerpAPI y procesa los resultados con Groq.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados procesados de la búsqueda
        """
        # Si no tenemos proveedor de búsqueda, volvemos al método de simulación
        if not self.search_provider:
            return self._simulate_web_search(query)
        
        try:
            # Extraer la keyword con Groq
            system_prompt = get_keyword_extraction_prompt()
            
            keyword_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ]
            )
            content_str = keyword_response.choices[0].message.content or ""
            
            # Validar que content_str contiene un JSON válido
            try:
                keyword_json = json.loads(content_str)
                keyword = keyword_json.get("keyword", query)
            except json.JSONDecodeError:
                # Si no podemos parsear el JSON, usamos la consulta original
                print(f"Error decodificando JSON de respuesta keyword: {content_str}")
                keyword = query
            
            # Realizar búsqueda con SerpAPI
            search_results = self.search_provider.search(keyword)
            
            # Verificar si hay resultados
            if not search_results or "error" in search_results:
                error_msg = search_results.get("error", "Error desconocido en la búsqueda") if search_results else "No se obtuvieron resultados de búsqueda"
                print(f"Error en búsqueda SerpAPI: {error_msg}")
                return {"error": error_msg, "success": False}
            
            answer_box = search_results.get("answer_box", {})
            organic_results = search_results.get("organic_results", [])
            
            # Preparar contenido para procesar con Groq
            content_to_process = ""
            
            if (answer_box):
                content_to_process += f"ANSWER BOX: {json.dumps(answer_box, indent=2)}\n\n"
            
            if organic_results and len(organic_results) > 0:
                content_to_process += "TOP RESULTS:\n"
                for idx, result in enumerate(organic_results[:5]):  # Tomamos los primeros 5 resultados
                    content_to_process += f"{idx+1}. {result.get('title', 'No Title')}: {result.get('snippet', 'No Snippet')}\n"
            
            if not content_to_process:
                return {"error": "No se encontraron resultados relevantes", "success": False}
            
            # Procesar los resultados con Groq
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
            print(f"Error en búsqueda web con Groq y SerpAPI: {str(e)}")
            # Si falla la búsqueda con SerpAPI, intentamos la simulación
            return self._simulate_web_search(query)
    
    def _simulate_web_search(self, query: str) -> Dict[str, Any]:
        """
        Método de respaldo que simula una búsqueda web cuando SerpAPI no está disponible.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados simulados de la búsqueda
        """
        try:
            system_prompt = get_web_search_prompt()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Búsqueda web: {query}"}
                ]
            )
            
            return {
                "content": response.choices[0].message.content,
                "success": True
            }
            
        except Exception as e:
            print(f"Error en búsqueda simulada con Groq: {str(e)}")
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
            # Realizar la búsqueda web (ahora usando SerpAPI si está disponible)
            search_result = self.search_web(query)
            
            if not search_result.get("success", False):
                from .prompts import get_fallback_content
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
            print(f"Error al generar contenido con Groq: {str(e)}")
            from .prompts import get_fallback_content
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