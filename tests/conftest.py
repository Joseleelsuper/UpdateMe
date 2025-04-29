import unittest
from app import app

class TestBase(unittest.TestCase):
    """Clase base para las pruebas unitarias de la aplicación Flask.
    Esta clase configura la aplicación para pruebas y proporciona un cliente de prueba.

    Args:
        unittest (unittest.TestCase): Clase base de unittest para crear pruebas unitarias.
    """
    
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