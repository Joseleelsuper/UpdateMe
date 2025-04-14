import unittest
from app import app

class TestBase(unittest.TestCase):
    """Clase base para todas las pruebas de la aplicación Flask."""
    
    def setUp(self):
        """Configurar para cada prueba."""
        self.app = app
        self.app.config.update({
            "TESTING": True,
            "WTF_CSRF_ENABLED": False  # Desactiva CSRF para pruebas (cuando implementes formularios)
        })
        self.client = self.app.test_client()
        self.runner = self.app.test_cli_runner()
        
    def tearDown(self):
        """Limpiar después de cada prueba."""
        pass  # Puedes añadir limpieza si es necesario