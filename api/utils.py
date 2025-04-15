"""
Este archivo contiene utilidades para validación de datos y otras funciones auxiliares.
"""
import re

# --- Utilidad para validar email ---
EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def is_valid_email(email):
    """Valida que un string tenga formato de email válido."""
    return EMAIL_REGEX.match(email) is not None