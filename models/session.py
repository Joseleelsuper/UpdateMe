from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from bson import ObjectId

@dataclass
class Session:
    _id: ObjectId  # ID único de la sesión
    user_id: ObjectId  # ID del usuario al que pertenece la sesión
    token: str  # Token JWT u otro token de autenticación
    created_at: datetime  # Timestamp de creación
    expires_at: datetime  # Timestamp de expiración
    user_agent: Optional[str] = None  # Información del navegador/dispositivo
    ip_address: Optional[str] = None  # Dirección IP del usuario
    is_active: bool = True  # Si la sesión está activa o ha sido invalidada manualmente
    
    def to_dict(self):
        """Convierte la instancia a un diccionario para almacenar en MongoDB"""
        return self.__dict__