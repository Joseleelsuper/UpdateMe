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
from api.serviceAi.prompts import get_news_summary_prompt, get_web_search_prompt

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
        
    title = _('UpdateMe - Weekly Tech & AI Newsletter')
    # Metadatos SEO para la página principal
    meta = {
        'meta_description': _('UpdateMe: La newsletter semanal que te mantiene al día con la tecnología y la IA. Recibe los resúmenes más relevantes en tu correo.'),
        'meta_keywords': 'newsletter, tecnología, IA, inteligencia artificial, noticias tech, resumen semanal',
        'canonical_url': url_for('main.page.index', _external=True),
    }
    
    return render_template("index.html", title=title, **meta)

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
    title = _('UpdateMe - Terms & Conditions')
    # Metadatos SEO para términos y condiciones
    meta = {
        'meta_description': _('Términos y condiciones de uso de UpdateMe. Información legal sobre el uso de nuestra newsletter y servicios.'),
        'meta_keywords': 'términos, condiciones, legal, servicios, newsletter',
        'canonical_url': url_for('main.page.terms_and_conditions', _external=True),
        'meta_robots': 'index, nofollow'
    }
    return render_template('terms-and-conditions.html', title=title, **meta)

@page_bp.route("/privacy-policy")
def privacy_policy():
    """
    Renderiza la página de política de privacidad.
    """
    title = _('UpdateMe - Privacy Policy')
    # Metadatos SEO para política de privacidad
    meta = {
        'meta_description': _('Política de privacidad de UpdateMe. Conoce cómo gestionamos y protegemos tus datos personales.'),
        'meta_keywords': 'privacidad, protección de datos, política, newsletter, RGPD',
        'canonical_url': url_for('main.page.privacy_policy', _external=True),
        'meta_robots': 'index, nofollow'
    }
    return render_template('privacy-policy.html', title=title, **meta)

@page_bp.route("/register")
def register():
    # Metadatos SEO para la página de registro
    meta = {
        'meta_description': _('Regístrate en UpdateMe y recibe resúmenes semanales de tecnología e IA personalizados para ti.'),
        'meta_keywords': 'registro, cuenta, newsletter tecnología, IA personalizada',
        'canonical_url': url_for('main.page.register', _external=True),
    }
    return render_template("register.html", title=_("title_register_page"), **meta)

@page_bp.route("/login")
def login():
    """
    Renderiza la página de inicio de sesión.
    """
    title = _('UpdateMe - Login')
    # Metadatos SEO para la página de login
    meta = {
        'meta_description': _('Accede a tu cuenta de UpdateMe y gestiona tu newsletter personalizada de tecnología e IA.'),
        'meta_keywords': 'login, acceso, cuenta, newsletter tecnología',
        'canonical_url': url_for('main.page.login', _external=True),
    }
    return render_template('login.html', title=title, **meta)

@page_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Ruta para la página del panel de control del usuario
    """
    
    # Obtener idioma actual
    language = g.user.get("language", "es")
    
    # Obtener los prompts predeterminados
    default_prompts = {
        "news_summary": get_news_summary_prompt(language),
        "web_search": get_web_search_prompt(language)
    }
    
    # Obtener los prompts personalizados del usuario
    prompts_id = g.user.get("prompts")
    user_prompts = db.prompts.find_one({"_id": prompts_id}) if prompts_id else {}
    
    return render_template(
        "dashboard.html", 
        user=g.user, 
        user_prompts=user_prompts,
        default_prompts=default_prompts
    )

@page_bp.route("/pricing")
def pricing():
    """
    Renderiza la página de precios.
    """
    title = _('UpdateMe - Pricing')
    # Metadatos SEO para la página de precios
    meta = {
        'meta_description': _('Conoce nuestros planes y precios para recibir resúmenes semanales de tecnología e IA. Escoge el que mejor se adapte a ti.'),
        'meta_keywords': 'precios, planes, suscripción, newsletter tecnología, IA',
        'canonical_url': url_for('main.page.pricing', _external=True),
    }
    return render_template('pricing.html', title=title, **meta)