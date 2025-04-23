"""
Implementación del proveedor SerpAPI para búsquedas web.
"""

import requests
import json
from typing import Dict, Any, Optional

class SerpAPIProvider:
    """
    Proveedor de servicio de búsqueda web usando la API de SerpAPI.
    
    SerpAPI es un servicio que permite realizar búsquedas en Google y otros motores
    de búsqueda de forma programática, devolviendo los resultados en formato JSON.
    """

    def __init__(self, api_key: str, engine: str = "google"):
        """
        Inicializa el proveedor de búsqueda SerpAPI.
        
        Args:
            api_key: Clave API de SerpAPI
            engine: Motor de búsqueda a utilizar (google, bing, yahoo, etc.)
        """
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        self.engine = engine
    
    def search(self, query: str, user_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Realiza una búsqueda web usando SerpAPI.
        
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
                "search_type": "news",
                "safe_search": "off",
                "time_range": "week",
                "include_domains": [],
                "exclude_domains": []
            }
            
            # Aplicar configuración personalizada del usuario si existe
            if user_config:
                config.update({k: v for k, v in user_config.items() if k in config})
            
            # Convertir configuración a parámetros de SerpAPI
            search_type = config["search_type"]
            tbm = "nws" if search_type == "news" else "isch" if search_type == "images" else "vid" if search_type == "videos" else None
                
            # Convertir el rango de tiempo al formato que espera SerpAPI
            time_map = {
                "day": "d",
                "week": "w",
                "month": "m",
                "year": "y"
            }
            tbs = f"qdr:{time_map.get(config['time_range'], 'w')}" if config['time_range'] in time_map else None
            
            # Construir los parámetros de la solicitud
            params = {
                "engine": self.engine,
                "q": query,
                "api_key": self.api_key,
                "gl": "es",       # Región geográfica (España)
                "hl": "es",       # Idioma de la interfaz
                "num": config["max_results"],  # Número de resultados
                "safe": config["safe_search"]  # Filtro de contenido
            }
            
            # Añadir tbm si se ha especificado un tipo de búsqueda
            if tbm:
                params["tbm"] = tbm
                
            # Añadir tbs si se ha especificado un rango de tiempo
            if tbs:
                params["tbs"] = tbs
                
            # Construir filtros de dominio si existen
            domain_filters = []
            if config["include_domains"]:
                for domain in config["include_domains"]:
                    domain_filters.append(f"site:{domain}")
            if config["exclude_domains"]:
                for domain in config["exclude_domains"]:
                    domain_filters.append(f"-site:{domain}")
                    
            # Añadir filtros de dominio a la consulta si existen
            if domain_filters:
                params["q"] = f"{query} {' '.join(domain_filters)}"
                
            # Realizar la solicitud
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error en la solicitud a SerpAPI: {str(e)}")
            return {"error": str(e), "results": [], "success": False}
        except json.JSONDecodeError:
            print("Error decodificando la respuesta JSON de SerpAPI")
            return {"error": "Error decodificando respuesta", "results": [], "success": False}