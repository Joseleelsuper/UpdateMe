"""
Implementación del proveedor Tavily para búsquedas web.
"""

import requests
import json
from typing import Dict, Any, Optional

class TavilyProvider:
    """
    Proveedor de servicio de búsqueda web usando la API de Tavily.
    
    Tavily ofrece una API de búsqueda web especializada para IA y LLM,
    permitiendo búsquedas actualizadas en tiempo real.
    """

    def __init__(
        self, 
        api_key: str, 
        search_depth: str = "advanced", 
        topic: str = "news", 
        time_range: str = "week", 
        include_raw_content: bool = True
    ):
        """
        Inicializa el proveedor de búsqueda Tavily.
        
        Args:
            api_key: Clave API de Tavily
            search_depth: Profundidad de la búsqueda ('basic', 'advanced')
            topic: Tema de búsqueda ('general', 'news', 'finance')
            time_range: Rango de tiempo para resultados ('day', 'week', 'month', 'year')
            include_raw_content: Si se debe incluir el contenido completo de las páginas
        """
        self.api_key = api_key
        self.base_url = "https://api.tavily.com/search"
        self.search_depth = search_depth
        self.topic = topic
        self.time_range = time_range
        self.include_raw_content = include_raw_content
    
    def search(self, query: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza una búsqueda web usando Tavily.
        
        Args:
            query: Consulta de búsqueda
            user_config: Configuración personalizada opcional (sobreescribe los valores por defecto)
            
        Returns:
            dict: Resultados de búsqueda
        """
        try:
            # Configuración base
            config = {
                "max_results": 5,
                "search_depth": self.search_depth,
                "topic": self.topic,
                "time_range": self.time_range,
                "include_raw_content": self.include_raw_content,
                "include_domains": [],
                "exclude_domains": []
            }
            
            # Aplicar configuración personalizada del usuario si existe
            if user_config:
                config.update({k: v for k, v in user_config.items() if k in config})
                
            # Construir los parámetros de la solicitud
            params = {
                "api_key": self.api_key,
                "query": query,
                "search_depth": config["search_depth"],
                "topic": config["topic"],
                "max_results": config["max_results"],
                "include_raw_content": config["include_raw_content"],
                "time_range": config["time_range"]
            }
            
            # Añadir dominios para incluir/excluir si están presentes
            if config["include_domains"]:
                params["include_domains"] = config["include_domains"]
            if config["exclude_domains"]:
                params["exclude_domains"] = config["exclude_domains"]
            
            # Realizar la solicitud
            response = requests.post(self.base_url, json=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud a Tavily: {str(e)}")
            return {"error": str(e), "results": [], "success": False}
        except json.JSONDecodeError:
            print("Error decodificando la respuesta JSON de Tavily")
            return {"error": "Error decodificando respuesta", "results": [], "success": False}