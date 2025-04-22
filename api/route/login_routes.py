from flask import Blueprint, jsonify, request, session, redirect, url_for
from api.database import users_collection
import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from flask_babel import gettext as _
from api.service.session_service import create_session, invalidate_session

# Crear el blueprint para las rutas de login
login_bp = Blueprint('login', __name__)

JWT_SECRET = os.environ.get('JWT_SECRET', '')

@login_bp.route('/login', methods=['POST'])
def login():
    """
    Maneja el inicio de sesión de usuarios.
    Espera un JSON con email y password.
    """
    # Obtener datos de la solicitud
    data = request.get_json()
    
    # Verificar que se proporcionaron los campos requeridos
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': _('Invalid request data.')
        }), 400
    
    email = data['email'].lower().strip()
    password = data['password']
    
    # Buscar el usuario por email
    user = users_collection.find_one({'email': email})
    
    # Verificar si el usuario existe y tiene contraseña
    if not user or not user.get('password'):
        return jsonify({
            'success': False,
            'message': _('Email or password incorrect.')
        }), 401
    
    # Verificar la contraseña
    try:
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            # Crear un JWT (aunque ahora usaremos nuestras sesiones personalizadas)
            expiration = datetime.now(timezone.utc) + timedelta(days=1)
            
            payload = {
                'user_id': str(user['_id']),
                'email': user['email'],
                'username': user['username'],
                'exp': expiration
            }
            
            token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
            
            # Crear sesión persistente (guardada en MongoDB)
            session_token, session_id = create_session(user['_id'])
            
            # Actualizar fecha de último inicio de sesión
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'last_login': datetime.now(timezone.utc).isoformat()}}
            )
            
            return jsonify({
                'success': True,
                'message': _('Login successful.'),
                'token': token,  # Seguimos enviando el JWT para mantener compatibilidad
                'redirect': '/dashboard'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': _('Email or password incorrect.')
            }), 401
            
    except Exception as e:
        print(f"Error during login: {e}")
        return jsonify({
            'success': False,
            'message': _('An error occurred during login. Please try again.')
        }), 500

@login_bp.route('/logout')
def logout():
    """
    Cierra la sesión del usuario y redirige a la página de inicio.
    """
    # Invalidar la sesión en la base de datos si existe
    if 'session_token' in session:
        invalidate_session(session['session_token'])
    
    # Eliminar datos de sesión de Flask
    session.pop('user_id', None)
    session.pop('session_token', None)
    
    return redirect(url_for('main.page.index'))