from flask import (
    Blueprint,
    render_template,
    send_from_directory,
    session,
    redirect,
    request,
    url_for,
)
from flask_babel import gettext as _

# Crear el blueprint para las rutas de página
page_bp = Blueprint('page', __name__)

@page_bp.route("/")
def home():
    return render_template("index.html", title=_("title_homepage"))

@page_bp.route("/static/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)

@page_bp.route("/change_language/<language>")
def change_language(language):
    session["language"] = language
    return redirect(request.referrer or url_for('main.page.home'))

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
