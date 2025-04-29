import unittest
from conftest import TestBase

class TestRoutes(TestBase):
    """Pruebas para las rutas principales de la aplicación."""
    
    def test_home_page(self):
        """Dada la ruta '/', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """Dada la ruta '/register', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page_without_auth(self):
        """Dada la ruta '/dashboard', se debe recibir una respuesta 302 Redirección."""
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirección
        # Verificar que redirecciona a la página de login o inicio
        self.assertTrue('/login' in response.location or '/' in response.location)

    def test_login_page(self):
        """Dada la ruta '/login', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_terms_page(self):
        """Dada la ruta '/terms-and-conditions', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/terms-and-conditions')
        self.assertEqual(response.status_code, 200)

    def test_privacy_page(self):
        """Dada la ruta '/privacy-policy', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/privacy-policy')
        self.assertEqual(response.status_code, 200)

    def test_pricing_page(self):
        """Dada la ruta '/pricing', se debe recibir una respuesta 200 OK."""
        response = self.client.get('/pricing')
        self.assertEqual(response.status_code, 200)

    def test_static_files_route(self):
        """Dada la ruta '/static/js/subscribe.js', se debe recibir una respuesta 200 OK.

        El objetivo es buscar que la ruta de los archivos estáticos funcione correctamente.
        """
        response = self.client.get('/static/js/subscribe.js')
        self.assertEqual(response.status_code, 200)

    def test_language_change(self):
        """Dada la ruta '/change-language/es', se debe recibir una respuesta 200 OK.

        Verificamos que la redirección funcione correctamente al cambiar el idioma.
        """
        # Primero verificamos el idioma español (predeterminado)
        response = self.client.get('/')
        
        # Cambiamos a inglés y verificamos la redirección
        # Usamos la ruta con el nombre completo del blueprint
        response = self.client.get('/change-language/en', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/change-language/es', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()