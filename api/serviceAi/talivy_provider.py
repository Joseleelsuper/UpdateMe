"""
Implementación de Tavily como proveedor de búsqueda web.
"""
from typing import Dict, Any
from tavily import TavilyClient

from .base import WebSearchProvider


class TavilyProvider(WebSearchProvider):
    """
    Implementación del proveedor de búsqueda Tavily.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de búsqueda Tavily.
        
        Args:
            api_key: La clave API de Tavily
            kwargs: Parámetros adicionales específicos para Tavily
        """
        self.api_key = api_key
        self.client = TavilyClient(api_key)
        self.search_depth = kwargs.get("search_depth", "advanced")
        self.topic = kwargs.get("topic", "news")
        self.time_range = kwargs.get("time_range", "week")
        self.include_raw_content = kwargs.get("include_raw_content", True)
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web con Tavily.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados de la búsqueda en formato de diccionario
        """
        try:
            response = self.client.search(
                query=query,
                topic=self.topic,
                search_depth=self.search_depth,
                time_range=self.time_range,
                include_raw_content=self.include_raw_content
            )
            return response
        except Exception as e:
            print(f"Error en búsqueda Tavily: {str(e)}")
            return {"error": str(e)}