"""
Implementación de SerpAPI como proveedor de búsqueda web.
"""
import requests
from typing import Dict, Any

from .base import WebSearchProvider


class SerpAPIProvider(WebSearchProvider):
    """
    Implementación del proveedor de búsqueda SerpAPI.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de búsqueda SerpAPI.
        
        Args:
            api_key: La clave API de SerpAPI
            kwargs: Parámetros adicionales
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search.json"
        
    def search(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web con SerpAPI.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados de la búsqueda en formato de diccionario
        """
        url = f"{self.base_url}?q={query}&api_key={self.api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Levantar excepción si hay error HTTP
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error en búsqueda SerpAPI: {str(e)}")
            return {"error": str(e)}