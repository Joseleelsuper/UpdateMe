"""
Este archivo contiene utilidades para validación de datos y otras funciones auxiliares.
"""
import re

# --- Utilidad para validar email ---
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def is_valid_email(email):
    """Valida que un string tenga formato de email válido."""
    return EMAIL_REGEX.match(email) is not None

# --- Utilidades para conversión de dataclasses a diccionarios ---
def dataclass_to_dict(obj):
    """
    Convierte cualquier dataclass a un diccionario.
    Función genérica para cualquier dataclass.
    
    Args:
        obj: Instancia de dataclass a convertir
        
    Returns:
        dict: Representación como diccionario
    """
    return obj.__dict__.copy()

def session_to_dict(session):
    """
    Convierte una instancia de Session a diccionario para MongoDB.
    
    Args:
        session: Instancia de Session
        
    Returns:
        dict: Representación como diccionario
    """
    return dataclass_to_dict(session)

def prompts_to_dict(prompts):
    """
    Convierte una instancia de Prompts a diccionario para MongoDB.
    
    Args:
        prompts: Instancia de Prompts
        
    Returns:
        dict: Representación como diccionario
    """
    return dataclass_to_dict(prompts)