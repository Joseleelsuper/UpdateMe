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
    """ID único de la entrada en la caché."""

    cache_key: str
    """Clave única para identificar la entrada en la caché."""

    response: Union[Dict[str, Any], str]
    """Respuesta de la API externa almacenada en la caché.

    Sirve para obtener al completo la respuesta de la API sin necesidad de volver a
    realizar la llamada. Puede ser un diccionario o una cadena de texto.
    """

    created_at: datetime
    """Fecha y hora en que se creó la entrada en la caché.

    Sirve para saber a qué día pertenece la entrada y si es necesario eliminarla
    o no. Se utiliza para la limpieza de entradas antiguas.
    """

    created_date: str
    """Fecha de creación de la entrada en formato YYYY-MM-DD.

    Lo mismo que el campo `created_at`, pero en formato de cadena de texto.
    """

    provider_type: str
    """Tipo de proveedor de la API externa.

    Puede ser una unión del nombre de la IA y su servicio, como por ejemplo:
    tavily_search
    """

    query: Optional[str] = None
    """Consulta realizada a la API externa.

    Es bueno guardarlo por si algún usuario utilizar la misma consulta y
    no es necesario volver a realizar la llamada a la API.
    """

    tags: List[str] = field(default_factory=list)
    """Etiquetas asociadas a la entrada en la caché.

    No se utiliza mucho, pero es bueno tenerlo por si se quiere filtrar por etiquetas.
    """

    ttl_days: int = 7
    """Tiempo de vida de la entrada en la caché en días."""
