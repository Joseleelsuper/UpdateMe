"""
Este archivo contiene las rutas (endpoints) de la API.
"""

from flask import Blueprint, jsonify, request, g
from api.database import db, users_collection
from flask_babel import gettext as _
from api.auth import login_required
from maintenance import process_pending_emails
import os

from api.route.page_routes import page_bp
from api.route.subscribe_routes import subscribe_bp
from api.route.translations_routes import translations_bp
from api.route.register_routes import register_bp
from api.route.login_routes import login_bp
from api.route.subscription_routes import subscription_routes  
from api.route.profile_routes import profile_bp  # Importar el nuevo blueprint de perfil

# Blueprint principal 
# Importante: configuramos url_prefix='/' para que no afecte a las rutas base
main_bp = Blueprint('main', __name__, url_prefix='/')

# Registrar todos los blueprints en el principal
main_bp.register_blueprint(page_bp)
main_bp.register_blueprint(subscribe_bp)
main_bp.register_blueprint(translations_bp)
main_bp.register_blueprint(register_bp)
main_bp.register_blueprint(login_bp)
main_bp.register_blueprint(profile_bp)  # Registrar el blueprint de perfil

# Blueprint para APIs
api_bp = Blueprint('api', __name__, url_prefix='/api')

# nuevo: registrar rutas de Stripe bajo api_bp para /api/subscription
api_bp.register_blueprint(subscription_routes)

# Función para registrar los blueprints en la aplicación Flask
def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

@api_bp.route('/user/preferences', methods=['POST'])
@login_required
def update_user_preferences():
    """
    Actualiza las preferencias del usuario
    """
    # Restringir a usuarios free
    if g.user.get("role") == "free":
        return jsonify({"success": False, "message": _("This feature is only available for premium users.")}), 403

    data = request.get_json()
    allowed_fields = ['language', 'ai_provider', 'search_provider']
    
    # Filtrar solo los campos permitidos
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({"success": False, "message": _("No valid fields to update")}), 400
    
    try:
        # Actualizar preferencias en la base de datos
        users_collection.update_one(
            {"_id": g.user["_id"]},  # Usar g.user["_id"] para consistencia
            {"$set": update_data}
        )
        return jsonify({"success": True, "message": _("Preferences updated successfully")})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/user/prompts', methods=['POST'])
@login_required
def update_user_prompts():
    """
    Actualiza los prompts personalizados del usuario y las configuraciones de búsqueda web
    """

    # Restringir a usuarios free
    if g.user.get("role") == "free":
        return jsonify({"success": False, "message": _("premiumUserOnly")}), 403

    data = request.get_json()
    allowed_fields = [
        'openai_prompt', 'groq_prompt', 'deepseek_prompt', 
        'tavily_prompt', 'serpapi_prompt',
        'tavily_config', 'serpapi_config'
    ]
    
    # Filtrar solo los campos permitidos
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        return jsonify({"success": False, "message": _("No valid prompts to update")}), 400
    
    # Validar el límite de caracteres para el prompt de Tavily
    if 'tavily_prompt' in update_data and len(update_data['tavily_prompt']) > 400:
        return jsonify({"success": False, "message": _("Tavily prompt exceeds the 400 character limit")}), 400
    
    try:
        # Obtener el usuario de g.user (ya establecido por el decorador login_required)
        user = g.user
        if not user or not user.get("prompts"):
            return jsonify({"success": False, "message": _("User or prompts not found")}), 404
        
        # Actualizar prompts en la base de datos
        db.prompts.update_one(
            {"_id": user["prompts"]},
            {"$set": update_data}
        )
        
        return jsonify({"success": True, "message": _("Prompts updated successfully")})
    except Exception as e:
        print(f"Error al actualizar prompts: {str(e)}")
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/user/prompts/reset', methods=['POST'])
@login_required
def reset_user_prompts():
    """
    Restablece los prompts del usuario a los valores predeterminados basados en el idioma del usuario
    """
    try:
        # Obtener el usuario y su ID de prompts
        user = g.user
        if not user or not user.get("prompts"):
            return jsonify({"success": False, "message": _("User or prompts not found")}), 404
        
        # Obtener los prompts predeterminados según el idioma del usuario
        from api.serviceAi.prompts import get_news_summary_prompt, get_tavily_search_prompt, get_serpapi_search_prompt, get_default_search_configs
        language = user.get("language", "es")
        news_summary = get_news_summary_prompt(language)
        tavily_prompt = get_tavily_search_prompt(language)
        serpapi_prompt = get_serpapi_search_prompt(language)
        default_configs = get_default_search_configs()
        
        # Restablecer todos los prompts y configuraciones a valores predeterminados
        reset_data = {
            "openai_prompt": news_summary,
            "groq_prompt": news_summary,
            "deepseek_prompt": news_summary,
            "tavily_prompt": tavily_prompt,
            "serpapi_prompt": serpapi_prompt,
            "tavily_config": default_configs["tavily"],
            "serpapi_config": default_configs["serpapi"]
        }
        
        db.prompts.update_one(
            {"_id": user["prompts"]},
            {"$set": reset_data}
        )
        return jsonify({"success": True, "message": _("promptsReset")})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@api_bp.route('/maintenance/send-weekly-emails', methods=['POST'])
def trigger_weekly_emails():
    """
    Endpoint para activar el envío de correos semanales.
    Debe estar protegido por una clave de API o token para evitar acceso no autorizado.
    """
    # Verificar autenticación
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != os.environ.get('MAINTENANCE_API_KEY'):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    try:
        # Procesar correos pendientes con un intervalo de 7 días
        total, success, errors = process_pending_emails(days_interval=6)
        
        return jsonify({
            "success": True,
            "message": f"Proceso completado: {total} usuarios procesados, {success} éxitos, {errors} errores"
        })
    except Exception as e:
        print(f"Error en el proceso de envío de correos: {str(e)}")
        return jsonify({
            "success": False, 
            "message": f"Error: {str(e)}"
        }), 500
