from flask import request, session
from datetime import datetime, timedelta
from bson import ObjectId
import secrets
from models.session import Session
from api.database import db

# Colección para las sesiones
sessions_collection = db["sessions"]

# Crear índice TTL (Time To Live) para la expiración automática de sesiones
def create_session_indexes():
    """
    Crea un índice TTL en la colección de sesiones para la expiración automática.
    Debe ejecutarse una sola vez durante la inicialización de la aplicación.
    """
    # Este índice eliminará automáticamente los documentos cuando expires_at sea alcanzado
    sessions_collection.create_index("expires_at", expireAfterSeconds=0)
    
    # Índice para búsqueda rápida por token
    sessions_collection.create_index("token", unique=True)
    
    # Índice para búsqueda rápida por user_id
    sessions_collection.create_index("user_id")

def create_session(user_id, session_duration_minutes=300):
    """
    Crea una nueva sesión para el usuario y la guarda en MongoDB.
    
    Args:
        user_id (ObjectId): ID del usuario
        session_duration_minutes (int): Duración de la sesión en minutos
    
    Returns:
        tuple: (token, session_id)
    """
    # Generar token seguro
    token = secrets.token_hex(32)
    
    # Calcular tiempo de expiración
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=session_duration_minutes)
    
    # Crear documento de sesión
    session_id = ObjectId()
    session_doc = Session(
        _id=session_id,
        user_id=ObjectId(user_id),
        token=token,
        created_at=created_at,
        expires_at=expires_at,
        user_agent=request.user_agent.string if request.user_agent else None,
        ip_address=request.remote_addr
    ).to_dict()
    
    # Guardar en MongoDB
    sessions_collection.insert_one(session_doc)
    
    # Guardar en la sesión de Flask - CONVERTIR ObjectId a string para que sea serializable
    session['user_id'] = str(user_id)
    session['session_token'] = token
    
    return token, session_id

def verify_session(token):
    """
    Verifica si una sesión es válida.
    
    Args:
        token (str): Token de sesión a verificar
    
    Returns:
        dict|None: Documento de usuario si la sesión es válida, None si no
    """
    # Buscar sesión por token
    session_doc = sessions_collection.find_one({
        "token": token,
        "is_active": True,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    if session_doc:
        # Sesión válida, obtener usuario
        from api.database import users_collection
        user = users_collection.find_one({"_id": session_doc["user_id"]})
        return user
    
    return None

def extend_session(token, session_duration_minutes=300):
    """
    Extiende la duración de una sesión existente.
    
    Args:
        token (str): Token de sesión a extender
        session_duration_minutes (int): Nueva duración en minutos desde ahora
    
    Returns:
        bool: True si se extendió correctamente, False si no
    """
    new_expiration = datetime.utcnow() + timedelta(minutes=session_duration_minutes)
    
    result = sessions_collection.update_one(
        {"token": token, "is_active": True},
        {"$set": {"expires_at": new_expiration}}
    )
    
    return result.modified_count > 0

def invalidate_session(token):
    """
    Invalida una sesión específica.
    
    Args:
        token (str): Token de sesión a invalidar
    
    Returns:
        bool: True si se invalidó correctamente, False si no
    """
    result = sessions_collection.update_one(
        {"token": token},
        {"$set": {"is_active": False}}
    )
    
    return result.modified_count > 0

def invalidate_all_user_sessions(user_id):
    """
    Invalida todas las sesiones activas de un usuario.
    
    Args:
        user_id (ObjectId): ID del usuario
    
    Returns:
        int: Número de sesiones invalidadas
    """
    result = sessions_collection.update_many(
        {"user_id": ObjectId(user_id), "is_active": True},
        {"$set": {"is_active": False}}
    )
    
    return result.modified_count

def get_user_active_sessions(user_id):
    """
    Obtiene todas las sesiones activas de un usuario.
    
    Args:
        user_id (ObjectId): ID del usuario
    
    Returns:
        list: Lista de sesiones activas
    """
    sessions = sessions_collection.find({
        "user_id": ObjectId(user_id),
        "is_active": True,
        "expires_at": {"$gt": datetime.utcnow()}
    })
    
    return list(sessions)

def cleanup_expired_sessions():
    """
    Limpia manualmente las sesiones expiradas. 
    Normalmente no es necesario llamar a esta función si el índice TTL está configurado,
    pero puede ser útil para mantenimiento o pruebas.
    
    Returns:
        int: Número de sesiones eliminadas
    """
    result = sessions_collection.delete_many({
        "expires_at": {"$lt": datetime.utcnow()}
    })
    
    return result.deleted_count