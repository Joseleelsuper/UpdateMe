"""
Punto de entrada principal para la aplicación UpdateMe.
Configura la aplicación Flask y registra todas las rutas y middleware.
"""
import os
import sys
from flask import Flask, g
from flask import session
from flask import send_from_directory
from flask_babel import Babel
from dotenv import load_dotenv
from api.routes import register_routes
from api.cache_manager import CacheManager
from api.session_middleware import session_middleware
from api.service.session_service import create_session_indexes

# Asegurar que el directorio raíz está en el path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Cargar variables de entorno
load_dotenv()

# Crear y configurar la aplicación Flask
app = Flask(__name__, 
            template_folder="../templates",
            static_folder="../static",
            static_url_path="/static")
            
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "development-key-change-in-production"
)
app.config["BABEL_DEFAULT_LOCALE"] = "es"

# Configurar ruta absoluta para traducciones
translations_path = os.path.join(root_dir, "translations")
app.config["BABEL_TRANSLATION_DIRECTORIES"] = translations_path

# Inicializar Babel para internacionalización
babel = Babel(app)

# Inicializar el sistema de caché
CacheManager.initialize_cache()

# Inicializar los índices para las sesiones
create_session_indexes()

@babel.localeselector
def get_locale():
    # Obtener locale de la sesión, o usar valor por defecto (es)
    if getattr(g, 'locale', None) is None:
        g.locale = session.get('language', 'es')
    return g.locale

# Rutas para archivos en la raíz del proyecto
@app.route('/robots.txt')
def robots():
    return send_from_directory(root_dir, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(root_dir, 'sitemap.xml')

@app.route('/favicon.ico')
def favicon_ico():
    return send_from_directory(root_dir, 'favicon.ico')

@app.route('/favicon.png')
def favicon_png():
    return send_from_directory(root_dir, 'favicon.png')

# Middleware para verificar sesiones en cada petición
app.before_request(session_middleware())

# Registrar todas las rutas
register_routes(app)

# Punto de entrada para WSGI
def entrypoint(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    app.run(debug=True)
