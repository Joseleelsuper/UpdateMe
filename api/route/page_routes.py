from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    session,
    redirect,
    request,
    url_for,
    g,
)
from flask_babel import gettext as _
from api.database import users_collection, db
from api.auth import login_required

# Crear el blueprint para las rutas de página
page_bp = Blueprint('page', __name__)

@page_bp.route("/")
def index():
    # Si el usuario tiene un token de sesión válido, redirigir a dashboard
    if 'session_token' in session:
        token = session['session_token']
        from api.service.session_service import verify_session
        user = verify_session(token)
        if user:
            return redirect(url_for('main.page.dashboard'))
    
    return render_template("index.html", title=_("title_homepage"))

@page_bp.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@page_bp.route("/change-language/<language>")
def change_language(language):
    # Guardar idioma en sesión
    if language in ['es', 'en']:
        session['language'] = language
        
        # Si el usuario está autenticado, actualizar su preferencia de idioma
        if 'user_id' in session:
            users_collection.update_one(
                {"_id": session['user_id']},
                {"$set": {"language": language}}
            )
    
    # Redirigir a la página desde la que se vino
    next_page = request.referrer or url_for('main.page.index')
    return redirect(next_page)

@page_bp.route("/terms-and-conditions")
def terms_and_conditions():
    """
    Renderiza la página de términos y condiciones.
    """
    title = _('Terms & Conditions - UpdateMe')
    return render_template('terms-and-conditions.html', title=title)

@page_bp.route("/privacy-policy")
def privacy_policy():
    """
    Renderiza la página de política de privacidad.
    """
    title = _('Privacy Policy - UpdateMe')
    return render_template('privacy-policy.html', title=title)

@page_bp.route("/register")
def register():
    return render_template("register.html", title=_("title_register_page"))

@page_bp.route("/login")
def login():
    """
    Renderiza la página de inicio de sesión.
    """
    title = _('UpdateMe - Login')
    return render_template('login.html', title=title)

@page_bp.route("/dashboard")
@login_required
def dashboard():
    """
    Renderiza la página del dashboard para usuarios autenticados.
    """
    # Obtener el usuario desde g.user (ya establecido por el decorador login_required)
    user = g.user
    
    # Obtener los prompts personalizados del usuario
    user_prompts = db.prompts.find_one({"_id": user.get("prompts")}) if user.get("prompts") else {}
    
    # Obtener los prompts por defecto del sistema
    from api.serviceAi.prompts import get_news_summary_prompt, get_web_search_prompt
    default_prompts = {
        "news_summary": get_news_summary_prompt(user.get("language", "es")),
        "web_search": get_web_search_prompt(user.get("language", "es"))
    }
    
    return render_template("dashboard.html", user=user, user_prompts=user_prompts, default_prompts=default_prompts)
