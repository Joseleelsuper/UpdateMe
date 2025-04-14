import unittest
from conftest import TestBase

class TestRoutes(TestBase):
    """Pruebas para las rutas principales de la aplicación."""
    
    def test_home_page(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita la página principal '/'
        THEN se debe recibir una respuesta 200 OK y verificar el contenido
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'UpdateMe', response.data)  # Verifica que el nombre de la app aparece en la página

if __name__ == '__main__':
    unittest.main()