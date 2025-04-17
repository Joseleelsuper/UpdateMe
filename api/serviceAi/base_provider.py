"""
Implementación base para proveedores de IA.
Contiene código común a todos los proveedores para evitar duplicación.
"""
import json
from typing import Dict, Any
from abc import abstractmethod
from bson.regex import Regex

from .base import AIProvider
from .prompts import get_news_summary_prompt, get_email_template, get_fallback_content
from ..database import db
from ..cache_manager import CacheManager


class BaseAIProvider(AIProvider):
    """
    Clase base que implementa funcionalidad común para todos los proveedores de IA.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA con su API key y parámetros comunes.
        
        Args:
            api_key: La clave API del proveedor
            kwargs: Parámetros adicionales específicos del proveedor
        """
        self.api_key = api_key
        self.model = kwargs.get("model", "default-model")
        
        # Configuración para proveedores de búsqueda
        self.serpapi_key = kwargs.get("serpapi_key", "")
        self.tavily_key = kwargs.get("tavily_key", "")
        self.search_provider_type = kwargs.get("search_provider", "serpapi")
        self.search_provider = None

        # Configuración específica para Tavily
        self.tavily_search_depth = kwargs.get("tavily_search_depth", "advanced")
        self.tavily_topic = kwargs.get("tavily_topic", "news")
        self.tavily_time_range = kwargs.get("tavily_time_range", "week")
        self.tavily_include_raw_content = kwargs.get("tavily_include_raw_content", True)
    
    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Método abstracto que debe ser implementado por cada proveedor.
        """
        pass
    
    @abstractmethod
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Método abstracto que debe ser implementado por cada proveedor.
        """
        pass
    
    def generate_news_summary(self, email: str) -> str:
        """
        Genera un resumen de noticias personalizado para el usuario.
        Implementación común para todos los proveedores.
        
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
        
        # Crear consulta para buscar noticias de tecnología e IA
        query = "Latest technology and AI news this week, top 5 most important news"
        
        try:
            # Realizar la búsqueda web
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
            return get_email_template(username, news_content, language)
            
        except Exception as e:
            print(f"Error al generar contenido: {str(e)}")
            return get_fallback_content(username, language)
    
    def _generate_fallback_content(self, email: str) -> str:
        """
        Genera un contenido de respaldo cuando falla la generación con IA.
        
        Args:
            email: Email del usuario
            
        Returns:
            str: Contenido de respaldo
        """
        username = email.split("@")[0]
        
        # Buscar al usuario en la base de datos
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        language = user_data.get("language", "es") if user_data else "es"
        
        return get_fallback_content(username, language)

    def _extract_user_language(self, email: str) -> str:
        """
        Extrae el idioma del usuario desde la base de datos.
        
        Args:
            email: Email del usuario
        
        Returns:
            str: Código de idioma ('es' o 'en')
        """
        user_data = db.users.find_one({"email": Regex(f"^{email}$", "i")})
        return user_data.get("language", "es") if user_data else "es"
    
    def _process_search_results(self, 
                                search_results: Dict[str, Any],
                                include_answer_box: bool = True,
                                max_results: int = 5) -> str:
        """
        Procesa los resultados de búsqueda en un formato útil para los LLMs.
        
        Args:
            search_results: Resultados de la búsqueda
            include_answer_box: Si se debe incluir la sección answer_box
            max_results: Número máximo de resultados a incluir
            
        Returns:
            str: Texto procesado con los resultados de búsqueda
        """
        content_to_process = ""
        
        # Incluir answer_box si existe y está habilitado
        answer_box = search_results.get("answer_box", {})
        if include_answer_box and answer_box:
            content_to_process += f"ANSWER BOX: {json.dumps(answer_box, indent=2)}\n\n"
        
        # Incluir resultados orgánicos
        organic_results = search_results.get("organic_results", [])
        if organic_results and len(organic_results) > 0:
            content_to_process += "TOP RESULTS:\n"
            for idx, result in enumerate(organic_results[:max_results]):
                content_to_process += f"{idx+1}. {result.get('title', 'No Title')}: {result.get('snippet', 'No Snippet')}\n"
        
        return content_to_process
    
    def _process_tavily_results(self,
                                search_results: Dict[str, Any],
                                max_results: int = 5) -> str:
        """
        Procesa los resultados de búsqueda de Tavily en un formato útil para los LLMs.
        
        Args:
            search_results: Resultados de la búsqueda de Tavily
            max_results: Número máximo de resultados a incluir
            
        Returns:
            str: Texto procesado con los resultados de búsqueda
        """
        content_to_process = ""
        
        # Incluir la respuesta generada por Tavily si está disponible
        if search_results.get("answer"):
            content_to_process += f"SUMMARY: {search_results.get('answer')}\n\n"
        
        # Incluir resultados de búsqueda
        results = search_results.get("results", [])
        if results and len(results) > 0:
            content_to_process += "TOP RESULTS:\n"
            for idx, result in enumerate(results[:max_results]):
                content_to_process += f"{idx+1}. {result.get('title', 'No Title')}: {result.get('content', 'No Content')}\n\n"
        
        # Incluir preguntas de seguimiento si están disponibles
        follow_up = search_results.get("follow_up_questions", [])
        if follow_up and len(follow_up) > 0:
            content_to_process += "\nRELATED QUESTIONS:\n"
            for idx, question in enumerate(follow_up[:3]):
                content_to_process += f"- {question}\n"
        
        return content_to_process
    
    def check_daily_cache(self, provider_type: str) -> bool:
        """
        Verifica si ya existen entradas de caché para el día de hoy
        para un tipo específico de proveedor de búsqueda.
        
        Args:
            provider_type: El tipo de proveedor de búsqueda (ej. "serpapi_search", "tavily_search")
            
        Returns:
            bool: True si existen entradas de caché para hoy, False en caso contrario
        """
        cached_items = CacheManager.get_today_cache_by_provider(provider_type)
        return len(cached_items) > 0
