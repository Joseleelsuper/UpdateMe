from dataclasses import dataclass, field
from typing import Dict, Any, List, Union, Optional
from datetime import datetime
from bson import ObjectId

@dataclass
class CacheEntry:
    """
    Modelo para representar una entrada en la caché.
    
    Almacena respuestas de APIs externas para reutilizarlas y reducir
    el número de llamadas a servicios externos.
    """
    _id: ObjectId
    cache_key: str  # Hash MD5 que identifica la consulta
    response: Union[Dict[str, Any], str]  # Contenido cacheado (puede ser diccionario o texto)
    created_at: datetime
    provider_type: str  # Tipo de proveedor (ej. "openai", "groq", "serpapi")
    query: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    ttl_days: int = 1  # Tiempo de vida en días (por defecto 1 día)
