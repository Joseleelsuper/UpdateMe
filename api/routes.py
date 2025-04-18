"""
Este archivo contiene las rutas (endpoints) de la API.
"""

from api.route.page_routes import register_page_routes
from api.route.subscribe_routes import register_subscribe_routes
from api.route.translations_routes import register_translations_routes


def register_routes(app):
    """Register all routes by delegating to specific modules."""
    register_page_routes(app)
    register_subscribe_routes(app)
    register_translations_routes(app)
