"""
Utilidades de autenticación para la aplicación.
"""
from functools import wraps
from flask import session, redirect, url_for, g
from api.service.session_service import verify_session

def login_required(f):
    """
    Decorador que verifica si el usuario ha iniciado sesión usando el sistema de sesiones persistentes.
    Si no ha iniciado sesión, redirige a la página de inicio.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Verificar por token de sesión
        if 'session_token' in session:
            token = session['session_token']
            user = verify_session(token)
            if user:
                # La sesión es válida, continuar
                # Almacenar el usuario en el contexto global para fácil acceso
                g.user = user
                return f(*args, **kwargs)
        
        # Si no hay sesión válida, redirigir a la página de login
        return redirect(url_for('main.page.login'))
    
    return decorated_function

def get_current_user_id():
    """
    Obtiene el ID del usuario actualmente autenticado.
    
    Returns:
        str|None: El ID del usuario autenticado o None si no hay usuario autenticado
    """
    if hasattr(g, 'user') and g.user and '_id' in g.user:
        return str(g.user['_id'])
    return None