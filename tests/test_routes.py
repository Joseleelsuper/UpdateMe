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

    def test_static_files_route(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita un archivo estático
        THEN se debe recibir una respuesta 200 OK
        """
        response = self.client.get('/static/js/subscribe.js')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'validateEmail', response.data)  # Verificar contenido del archivo JS

    def test_language_change(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se cambia el idioma
        THEN se debe actualizar el idioma en la sesión y redireccionar
        """
        # Primero verificamos el idioma español (predeterminado)
        response = self.client.get('/')
        self.assertIn(b'tecnolog\xc3\xada e IA', response.data)  # Texto en español
        
        # Cambiamos a inglés y verificamos la redirección
        response = self.client.get('/change_language/en', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'technology and AI content', response.data)  # Texto en inglés

if __name__ == '__main__':
    unittest.main()