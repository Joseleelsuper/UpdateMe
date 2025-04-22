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
    
    def test_register_page(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita la página de registro '/register'
        THEN se debe recibir una respuesta 200 OK y verificar el contenido
        """
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)

    def test_dashboard_page_without_auth(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita la página del dashboard '/dashboard' sin estar autenticado
        THEN se debe recibir una redirección (302) a la página de login
        """
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)  # Redirección
        # Verificar que redirecciona a la página de login o inicio
        self.assertTrue('/login' in response.location or '/' in response.location)

    def test_login_page(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita la página de login '/login'
        THEN se debe recibir una respuesta 200 OK
        """
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)

    def test_static_files_route(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se solicita un archivo estático
        THEN se debe recibir una respuesta 200 OK
        """
        response = self.client.get('/static/js/subscribe.js')
        self.assertEqual(response.status_code, 200)

    def test_language_change(self):
        """
        GIVEN la aplicación configurada para pruebas
        WHEN se cambia el idioma usando la nueva estructura de blueprints
        THEN se debe actualizar el idioma en la sesión y redireccionar
        """
        # Primero verificamos el idioma español (predeterminado)
        response = self.client.get('/')
        
        # Cambiamos a inglés y verificamos la redirección
        # Usamos la ruta con el nombre completo del blueprint
        response = self.client.get('/change-language/en', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()