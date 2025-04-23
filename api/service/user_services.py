from flask import session, g, jsonify
from bson import ObjectId
from datetime import datetime, timezone
import re
import bcrypt
from flask_babel import gettext as _
from api.database import users_collection, db
from api.utils import is_valid_email
from api.services import send_email, generate_news_summary, send_welcome_email
from models.user import User
from models.prompts import Prompts
from api.serviceAi.prompts import get_news_summary_prompt, get_web_search_prompt

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
    
    # Create a new ObjectId for the user's prompts
    prompts_id = ObjectId()
    
    # Cuando se crea un usuario nuevo, establecemos la fecha actual como último envío
    # para que se le envíe el primer resumen regular después de una semana
    current_time = datetime.now(timezone.utc)
    
    return User(
        _id=ObjectId(),
        username=username,
        email=email,
        password=hashed_password,
        created_at=current_time,
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
        prompts=prompts_id,
        last_email_sent=current_time
    ).__dict__

def create_prompts_document(user_id, prompts_id, language="es"):
    """
    Crear documento de prompts personalizado para un usuario
    
    Args:
        user_id: ID del usuario
        prompts_id: ID asignado al documento de prompts
        language: Idioma del usuario para los prompts por defecto
        
    Returns:
        dict: Documento de prompts listo para insertar
    """
    
    # Obtener prompts predeterminados según el idioma
    news_summary_prompt = get_news_summary_prompt(language)
    web_search_prompt = get_web_search_prompt(language)
    
    return Prompts(
        _id=prompts_id,
        openai_prompt=news_summary_prompt,
        groq_prompt=news_summary_prompt,
        deepseek_prompt=news_summary_prompt,
        tavily_prompt=web_search_prompt,
        serpapi_prompt=web_search_prompt
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
        
        # Crear y guardar el documento de prompts personalizado
        prompts_doc = create_prompts_document(user_doc["_id"], user_doc["prompts"])
        db.prompts.insert_one(prompts_doc)
        
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