from flask import session, request, redirect, url_for, g
from api.service.session_service import verify_session, extend_session

def session_middleware():
    """
    Middleware para verificar la sesión del usuario en cada petición.
    Debe ser registrado en la aplicación antes de manejar las rutas.
    """
    def middleware():
        # Ignorar rutas estáticas y de autenticación
        if request.path.startswith('/static') or request.path in ['/login', '/register', '/subscribe']:
            return None
        
        # Verificar si hay un token de sesión
        if 'session_token' in session:
            token = session['session_token']
            
            # Verificar si la sesión es válida
            user = verify_session(token)
            
            if user:
                # Sesión válida, extender duración automáticamente
                extend_session(token)
                
                # Almacenar el usuario en el contexto global para esta petición
                g.user = user
                g.user_id = user['_id']  # Este ya es un ObjectId desde MongoDB
                
                # Todo correcto, continuar con la petición
                return None
            else:
                # Sesión inválida o expirada, limpiar
                session.pop('user_id', None)
                session.pop('session_token', None)
        
        # Si es una ruta que requiere autenticación, redirigir al login
        if request.path in ['/dashboard'] or request.path.startswith('/api/user/'):
            return redirect(url_for('main.page.index'))
        
        # Para otras rutas, permitir el acceso sin autenticación
        return None
    
    return middleware