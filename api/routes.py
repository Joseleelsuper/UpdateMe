"""
Este archivo contiene las rutas (endpoints) de la API.
"""

from flask import Blueprint
from api.route.page_routes import page_bp
from api.route.subscribe_routes import subscribe_bp
from api.route.translations_routes import translations_bp
from api.route.register_routes import register_bp
from api.route.login_routes import login_bp

# Blueprint principal 
# Importante: configuramos url_prefix='/' para que no afecte a las rutas base
main_bp = Blueprint('main', __name__, url_prefix='/')

# Registrar todos los blueprints en el principal
main_bp.register_blueprint(page_bp)
main_bp.register_blueprint(subscribe_bp)
main_bp.register_blueprint(translations_bp)
main_bp.register_blueprint(register_bp)
main_bp.register_blueprint(login_bp)

# Función para registrar el blueprint en la aplicación Flask
def register_routes(app):
    app.register_blueprint(main_bp)
