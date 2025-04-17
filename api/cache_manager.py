"""
Sistema de caché para resultados de búsquedas web y consultas a la IA.
Reduce el número de llamadas a APIs externas reutilizando respuestas recientes.
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union, List
from bson import ObjectId
from pymongo import IndexModel, ASCENDING

from .database import cache_collection, db
from models.cache import CacheEntry

class CacheManager:
    """
    Gestiona la caché de respuestas de APIs externas.
    
    Guarda los resultados de búsquedas y consultas en MongoDB y los recupera
    cuando se realizan consultas similares dentro del mismo día.
    """
    
    @classmethod
    def initialize_cache(cls) -> None:
        """
        Inicializa la colección de caché y crea los índices necesarios.
        Este método debe ser llamado al iniciar la aplicación.
        """
        # Crear la colección si no existe
        if "cache" not in db.list_collection_names():
            db.create_collection("cache")
            print("Colección de caché creada correctamente")
        
        # Crear índices para mejorar el rendimiento de búsquedas
        indices = [
            IndexModel([("cache_key", ASCENDING)], unique=True),
            IndexModel([("created_date", ASCENDING)]),
            IndexModel([("provider_type", ASCENDING)])
        ]
        
        # Crear los índices en la colección
        try:
            cache_collection.create_indexes(indices)
            print("Índices de caché creados correctamente")
        except Exception as e:
            print(f"Error al crear índices de caché: {str(e)}")
    
    @staticmethod
    def generate_cache_key(query: str, provider_type: str, additional_params: Optional[Dict] = None) -> str:
        """
        Genera una clave única para la caché basada en la consulta, proveedor y fecha actual.
        
        Args:
            query: La consulta o prompt que se está procesando
            provider_type: El tipo de proveedor (ej. "openai", "groq", "serpapi", "tavily")
            additional_params: Parámetros adicionales para diferenciar consultas (opcional)
            
        Returns:
            Una cadena hash que sirve como clave única
        """
        # Normalizar la consulta: eliminar espacios extras y convertir a minúsculas
        normalized_query = query.strip().lower()
        
        # Obtener fecha actual (solo día, mes y año)
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Crear un diccionario con todos los parámetros para generar el hash
        hash_data = {
            "query": normalized_query,
            "provider": provider_type,
            "date": today_date
        }
        
        # Añadir parámetros adicionales si existen
        if additional_params:
            hash_data.update(additional_params)
        
        # Convertir a JSON y calcular el hash
        data_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    @staticmethod
    def get_from_cache(cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Recupera una respuesta de la caché si existe y es del día actual.
        
        Args:
            cache_key: La clave generada para identificar la consulta
            
        Returns:
            El resultado cacheado o None si no existe o no es de hoy
        """
        # Obtener la fecha actual (solo día, mes y año)
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar en la caché
        cached_item = cache_collection.find_one({
            "cache_key": cache_key,
            "created_date": today_date
        })
        
        if cached_item:
            return cached_item.get("response")
        
        return None
    
    @staticmethod
    def get_today_cache_by_provider(provider_type: str) -> List[Dict[str, Any]]:
        """
        Recupera todas las entradas de caché del día actual para un proveedor específico.
        
        Args:
            provider_type: El tipo de proveedor (ej. "openai", "groq", "serpapi", "tavily")
            
        Returns:
            Lista de resultados cacheados del día de hoy para ese proveedor
        """
        # Obtener la fecha actual (solo día, mes y año)
        today_date = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar todas las entradas para ese proveedor de hoy
        cached_items = list(cache_collection.find({
            "provider_type": provider_type,
            "created_date": today_date
        }))
        
        return cached_items
    
    @staticmethod
    def save_to_cache(cache_key: str, response: Union[Dict[str, Any], str], provider_type: str = "generic", query: Optional[str] = None, ttl_days: int = 1) -> None:
        """
        Guarda una respuesta en la caché utilizando el modelo CacheEntry.
        
        Args:
            cache_key: La clave generada para identificar la consulta
            response: La respuesta de la API que se guardará
            provider_type: Tipo de proveedor que generó la respuesta
            query: Consulta original (opcional)
            ttl_days: Tiempo de vida en días (por defecto 1 día)
        """
        # Eliminar entradas antiguas con la misma clave (si existen)
        cache_collection.delete_many({"cache_key": cache_key})
        
        # Obtener la fecha actual
        now = datetime.now()
        today_date = now.strftime("%Y-%m-%d")
        
        # Crear una nueva entrada de caché usando el modelo
        cache_entry = CacheEntry(
            _id=ObjectId(),
            cache_key=cache_key,
            response=response,
            created_at=now,
            created_date=today_date,
            provider_type=provider_type,
            query=query,
            tags=[provider_type],
            ttl_days=ttl_days
        )
        
        # Convertir a diccionario y guardar en la base de datos
        cache_collection.insert_one(cache_entry.__dict__)
    
    @staticmethod
    def clear_expired_cache(days_to_keep: int = 7) -> int:
        """
        Elimina entradas de caché antiguas.
        
        Args:
            days_to_keep: Número de días que se conservarán las entradas
            
        Returns:
            Número de documentos eliminados
        """
        # Calcular la fecha límite
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Eliminar documentos antiguos
        result = cache_collection.delete_many({"created_at": {"$lt": cutoff_date}})
        
        return result.deleted_count
