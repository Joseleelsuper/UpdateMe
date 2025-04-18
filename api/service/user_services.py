from flask import session, g, jsonify
from bson import ObjectId
from datetime import datetime, timezone
import re
import bcrypt
from flask_babel import gettext as _
from api.database import users_collection
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary, send_welcome_email
from models.user import User

def validate_email(email):
    """Validar formato de correo electrónico"""
    if not is_valid_email(email):
        return jsonify({
            "success": False,
            "message": _("invalidEmail")
        }), 400
    return None

def check_existing_email(email):
    """Verificar si un correo ya existe en la base de datos"""
    return users_collection.find_one({"email": email})

def validate_password(password):
    """Validar que la contraseña cumpla con los requisitos de seguridad"""
    if len(password) < 6:
        return jsonify({
            "success": False,
            "message": _("passwordLength")
        }), 400
    
    if not re.search(r'[A-Z]', password):
        return jsonify({
            "success": False,
            "message": _("passwordUppercase")
        }), 400
    
    if not re.search(r'[a-z]', password):
        return jsonify({
            "success": False,
            "message": _("passwordLowercase")
        }), 400
    
    if not re.search(r'[0-9]', password):
        return jsonify({
            "success": False,
            "message": _("passwordNumber")
        }), 400
    
    if not re.search(r'[_\W]', password):
        return jsonify({
            "success": False,
            "message": _("passwordSpecial")
        }), 400
    
    return None

def validate_username(username):
    """Validar que el nombre de usuario tenga el formato correcto"""
    if not username or not re.match(r'^[a-zA-Z0-9\s]+$', username):
        return jsonify({
            "success": False,
            "message": _("invalidUsername")
        }), 400
    return None

def hash_password(password):
    """Generar hash seguro de la contraseña"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_current_language():
    """Obtener el idioma actual del usuario desde la sesión o configuración global"""
    return session.get("language", g.get("locale", "es"))

def create_user_document(email, username=None, password=None):
    """
    Crear documento de usuario para la base de datos
    Si no se proporciona username, se genera uno a partir del correo
    """
    current_language = get_current_language()
    
    if username is None:
        username = email.split("@")[0]
    
    hashed_password = None
    if password:
        hashed_password = hash_password(password)
    
    return User(
        _id=ObjectId(),
        username=username,
        email=email,
        password=hashed_password,
        created_at=datetime.now(timezone.utc),
        role="free",
        email_verified=False,
        account_status="active",
        language=current_language,
        search_provider="tavily",
        ai_provider="groq",
        billing_address=None,
        last_login=None,
        subscription=None,
        payment_methods=[],
    ).__dict__

def send_welcome_emails(email):
    """Enviar correos de bienvenida y primer resumen"""
    try:
        send_welcome_email(email)
        try:
            summary = generate_news_summary(email)
            send_email(
                email,
                "UpdateMe: Tu resumen semanal de tecnología e IA",
                summary,
            )
        except Exception as e:
            print(f"Error enviando resumen completo: {str(e)}")
            # No lanzamos excepción si falla solo el resumen
    except Exception as e:
        print(f"Error enviando correo de bienvenida: {str(e)}")
        raise  # Relanzar la excepción para que sea manejada por el llamador

def create_new_user(email, username=None, password=None, send_emails=True):
    """
    Crear un nuevo usuario en la base de datos
    
    Args:
        email: Correo electrónico del usuario
        username: Nombre de usuario (opcional)
        password: Contraseña sin encriptar (opcional)
        send_emails: Si se deben enviar correos de bienvenida
    
    Returns:
        (response, status_code) o None si todo es exitoso
    """
    try:
        user_doc = create_user_document(email, username, password)
        
        # Enviar correos si se solicita
        if send_emails:
            try:
                send_welcome_emails(email)
            except Exception as e:
                print(f"Error enviando correos: {str(e)}")
                return jsonify({
                    "success": False,
                    "message": _("An unexpected error occurred. Please try again.")
                }), 500
        
        # Insertar el usuario en la base de datos
        users_collection.insert_one(user_doc)
        
        return None
    except Exception as e:
        print(f"Error creando usuario: {str(e)}")
        return jsonify({
            "success": False,
            "message": _("An unexpected error occurred. Please try again.")
        }), 500

def update_existing_user(user, username, password):
    """
    Actualizar usuario existente con nuevo nombre de usuario y contraseña
    
    Args:
        user: Documento de usuario existente
        username: Nuevo nombre de usuario
        password: Nueva contraseña sin encriptar
        
    Returns:
        (response, status_code) o None si todo es exitoso
    """
    try:
        hashed_password = hash_password(password)
        current_language = get_current_language()
        
        users_collection.update_one(
            {"email": user["email"]},
            {
                "$set": {
                    "username": username,
                    "password": hashed_password,
                    "role": user.get("role", "free"),
                    "email_verified": user.get("email_verified", False),
                    "account_status": "active",
                    "language": current_language
                }
            }
        )
        
        return None
    except Exception as e:
        print(f"Error actualizando usuario: {str(e)}")
        return jsonify({
            "success": False,
            "message": _("An unexpected error occurred. Please try again.")
        }), 500