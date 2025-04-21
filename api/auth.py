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
        
        # Si no hay sesión válida, redirigir a la página principal
        return redirect(url_for('main.page.index'))
    
    return decorated_function