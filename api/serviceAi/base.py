"""
Módulo base que define las interfaces abstractas para los servicios de IA.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """
    Clase abstracta que define la interfaz común para todos los proveedores de IA.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de IA con su API key y otros parámetros necesarios.
        
        Args:
            api_key: La clave API del proveedor
            kwargs: Parámetros adicionales específicos del proveedor
        """
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> str:
        """
        Genera contenido basado en un prompt utilizando el proveedor de IA.
        
        Args:
            prompt: El prompt o instrucción para generar contenido
            kwargs: Parámetros adicionales específicos para la generación
            
        Returns:
            El contenido generado como string
        """
        pass
    
    @abstractmethod
    def search_web(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web para obtener información actualizada.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados de la búsqueda en formato de diccionario
        """
        pass
    
    @abstractmethod
    def generate_news_summary(self, email: str) -> str:
        """
        Genera un resumen de noticias personalizado para el email del usuario.
        
        Args:
            email: El email del usuario
            
        Returns:
            El resumen de noticias formateado como un email
        """
        pass


class WebSearchProvider(ABC):
    """
    Clase abstracta para proveedores de búsqueda web.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa el proveedor de búsqueda con su API key.
        
        Args:
            api_key: La clave API del proveedor de búsqueda
            kwargs: Parámetros adicionales específicos del proveedor
        """
        pass
    
    @abstractmethod
    def search(self, query: str) -> Dict[str, Any]:
        """
        Realiza una búsqueda web con la consulta proporcionada.
        
        Args:
            query: La consulta de búsqueda
            
        Returns:
            Resultados de la búsqueda en formato de diccionario
        """
        pass