from datetime import datetime
from unittest.mock import MagicMock, patch
from conftest import TestBase
import json
import bcrypt
from bson import ObjectId
from api.database import users_collection


class TestRegister(TestBase):
    """Pruebas para la funcionalidad de registro de usuario."""

    def setUp(self):
        super().setUp()
        # Limpiamos cualquier usuario de test que pueda existir antes de cada prueba
        users_collection.delete_many({"email": {"$regex": "test.*@example.com"}})

    def tearDown(self):
        super().tearDown()
        # Limpiamos usuarios de test después de cada prueba
        users_collection.delete_many({"email": {"$regex": "test.*@example.com"}})

    @patch('resend.Emails.send')
    def test_successful_registration(self, mock_send_email: MagicMock):
        """Dados datos de registro válidos, se debe crear un nuevo usuario y enviar correos de bienvenida y resumen.

        Args:
            mock_send_email (MagicMock): Mock para la función de envío de correos.
        """
        # Configurar el mock para simular envío exitoso
        mock_send_email.return_value = {"id": "123456", "status": "success"}

        # Datos de registro válidos
        register_data = {
            "username": "testuser",
            "email": "testregister@example.com",
            "password": "Test123_password"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verificar que el usuario está en la base de datos
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNotNone(user)
        if user is not None:
            self.assertEqual(user.get("username"), register_data["username"])
            self.assertNotEqual(user.get("password"), register_data["password"])
            # Verificar que el hash de la contraseña es válido
            self.assertTrue(bcrypt.checkpw(
                register_data["password"].encode('utf-8'),
                user.get("password").encode('utf-8')
            ))

        # Verificar que se llamó a la función de enviar correo dos veces (bienvenida y resumen)
        self.assertEqual(mock_send_email.call_count, 2)

    @patch('resend.Emails.send')
    def test_registration_existing_subscriber(self, mock_send_email: MagicMock):
        """Dados datos de registro válidos, se debe actualizar el usuario existente y no enviar correos.

        Args:
            mock_send_email (MagicMock): Mock para la función de envío de correos.
        """
        # Crear usuario de prueba (suscriptor sin contraseña)
        test_email = "testsubscriber@example.com"
        users_collection.insert_one({
            "_id": ObjectId(),
            "email": test_email,
            "username": test_email.split("@")[0],  # Username generado automáticamente del email
            "created_at": "2025-04-15T00:00:00",
            "role": "free",
            "email_verified": False,
            "account_status": "active",
            "password": None
        })

        # Datos para actualización mediante registro
        register_data = {
            "username": "subscriberuser",
            "email": test_email,
            "password": "Subscriber123_"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta exitosa
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verificar que el usuario se actualizó correctamente
        user = users_collection.find_one({"email": test_email})
        self.assertIsNotNone(user)
        if user is not None:
            self.assertEqual(user.get("username"), register_data["username"])
            self.assertTrue(bcrypt.checkpw(
                register_data["password"].encode('utf-8'),
                user.get("password").encode('utf-8')
            ))

        # Verificar que no se enviaron correos ya que el usuario ya existía
        mock_send_email.assert_not_called()

    @patch('resend.Emails.send')
    def test_registration_existing_user(self, mock_send_email: MagicMock):
        """Dados datos de registro válidos, se debe recibir un error 409 si el email ya existe.
        Se debe verificar que el usuario no se modifique y que no se envíen correos.

        Args:
            mock_send_email (MagicMock): Mock para la función de envío de correos.
        """
        # Crear usuario de prueba (con contraseña)
        test_email = "testexisting@example.com"
        hashed_pw = bcrypt.hashpw("Existing123_".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        users_collection.insert_one({
            "_id": ObjectId(),
            "email": test_email,
            "username": "existinguser",
            "created_at": "2025-04-15T00:00:00",
            "role": "free",
            "email_verified": False,
            "account_status": "active",
            "password": hashed_pw
        })

        # Intentar registrar el mismo email
        register_data = {
            "username": "newusername",
            "email": test_email,
            "password": "NewPassword123_"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que el usuario no fue modificado
        user = users_collection.find_one({"email": test_email})
        self.assertIsNotNone(user)
        if user is not None:
            self.assertEqual(user.get("username"), "existinguser")
            self.assertEqual(user.get("password"), hashed_pw)

        # Verificar que no se envió ningún correo
        mock_send_email.assert_not_called()

    def test_invalid_username_format(self):
        """Dado un nombre de usuario con caracteres especiales no permitidos,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        # Probar con caracteres especiales no permitidos en el nombre de usuario
        register_data = {
            "username": "test@user!",
            "email": "test_invalid_username@example.com",
            "password": "Valid123_password"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que no se creó el usuario
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    def test_invalid_email_format(self):
        """Dado un email con formato inválido,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "invalid-email",
            "password": "Valid123_password"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que no se creó el usuario
        user = users_collection.find_one({"username": register_data["username"]})
        self.assertIsNone(user)

    def test_password_too_short(self):
        """Dado una contraseña demasiado corta (menos de 6 caracteres),
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "test_short_pw@example.com",
            "password": "Ab1_"  # Menos de 6 caracteres
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que no se creó el usuario
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    def test_password_no_uppercase(self):
        """Dado una contraseña sin letras mayúsculas,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "test_no_upper@example.com",
            "password": "password123_"  # Sin mayúscula
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que no se creó el usuario
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    def test_password_no_lowercase(self):
        """Dado una contraseña sin letras minúsculas,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "test_no_lower@example.com",
            "password": "PASSWORD123_"  # Sin minúscula
        }

        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    def test_password_no_number(self):
        """Dado una contraseña sin números,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "test_no_number@example.com",
            "password": "Password_"  # Sin número
        }

        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    def test_password_no_special_char(self):
        """Dado una contraseña sin caracteres especiales,
        se debe recibir un error 400 y el usuario no debe guardarse.
        """
        register_data = {
            "username": "validuser",
            "email": "test_no_special@example.com",
            "password": "Password123"  # Sin carácter especial
        }

        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

    @patch('resend.Emails.send')
    def test_email_sending_failure(self, mock_send_email: MagicMock):
        """Dados datos de registro válidos, si ocurre un error al enviar el correo,
        se debe recibir un error 500 y el usuario no debe guardarse.

        Args:
            mock_send_email (MagicMock): Mock para la función de envío de correos.
        """
        # Configurar el mock para simular un error de envío
        mock_send_email.side_effect = Exception("Error de envío simulado")

        register_data = {
            "username": "newvaliduser",
            "email": "test_email_fail@example.com",
            "password": "Valid123_password"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que el usuario NO está en la base de datos
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)
        
    @patch('api.service.user_services.create_user_document')
    def test_database_error(self, mock_create_user: MagicMock):
        """Dados datos de registro válidos, si ocurre un error en la base de datos,

        Args:
            mock_create_user (MagicMock): Mock para la función de creación de usuario en la base de datos.
        """
        # Simular error en la creación del documento
        mock_create_user.side_effect = Exception("Error de base de datos simulado")

        register_data = {
            "username": "dberroruser",
            "email": "test_db_error@example.com",
            "password": "Valid123_password"
        }

        # Enviar solicitud de registro
        response = self.client.post(
            '/register',
            data=json.dumps(register_data),
            content_type='application/json'
        )

        # Verificar respuesta de error
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que el usuario NO está en la base de datos
        user = users_collection.find_one({"email": register_data["email"]})
        self.assertIsNone(user)

class TestLogin(TestBase):
    """Pruebas para la funcionalidad de inicio de sesión."""

    def setUp(self):
        super().setUp()
        # Crear un usuario de prueba con contraseña hasheada para las pruebas de login
        from datetime import datetime
        
        self.test_email = "test_login@example.com"
        self.test_password = "Test123_login"
        self.test_username = "testlogin"
        self.hashed_pw = bcrypt.hashpw(self.test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insertar un usuario de prueba con ID como string para compatibilidad con los tests
        self.test_user_id = ObjectId()
        users_collection.insert_one({
            "_id": self.test_user_id,
            "email": self.test_email,
            "username": self.test_username,
            "created_at": datetime.now().isoformat(),
            "role": "free",
            "email_verified": False,
            "account_status": "active",
            "password": self.hashed_pw
        })

    def tearDown(self):
        super().tearDown()
        # Limpiar usuarios de test después de cada prueba
        users_collection.delete_many({"email": {"$regex": "test.*@example.com"}})

    def test_successful_login(self):
        """Dado un email y contraseña válidos,
        se debe recibir un código 200 y un token JWT en la respuesta.
        """
        # Mock para crear_session
        with patch('api.route.login_routes.create_session') as mock_create_session:
            # Configurar el mock para simular la creación de sesión exitosa
            mock_session_token = "mock_session_token"
            mock_session_id = ObjectId()
            mock_create_session.return_value = (mock_session_token, mock_session_id)

            # Datos de login válidos
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }

            # Mock de _() para asegurar respuestas en inglés durante las pruebas
            with patch('api.route.login_routes._') as mock_gettext:
                mock_gettext.side_effect = lambda x: {
                    'Login successful.': 'Login successful.',
                    'Email or password incorrect.': 'Email or password incorrect.',
                    'Invalid request data.': 'Invalid request data.',
                    'An error occurred during login. Please try again.': 'An error occurred during login. Please try again.'
                }.get(x, x)  # Devuelve el texto en inglés o el original si no está mapeado
                
                # Enviar solicitud de login
                response = self.client.post(
                    '/login',
                    data=json.dumps(login_data),
                    content_type='application/json'
                )

                # Verificar respuesta exitosa
                self.assertEqual(response.status_code, 200)
                data = json.loads(response.data)
                self.assertTrue(data['success'])
                self.assertEqual(data['message'], 'Login successful.')
                self.assertIn('token', data)  # Debe contener un token JWT
                self.assertEqual(data['redirect'], '/dashboard')

                # Verificar que se llamó a create_session con el ID correcto del usuario
                mock_create_session.assert_called_once_with(self.test_user_id)

    def test_login_wrong_password(self):
        """Dado un email y una contraseña incorrectos,
        se debe recibir un código 401 y un mensaje de error adecuado.
        """
        login_data = {
            "email": self.test_email,
            "password": "WrongPassword123_"  # Contraseña incorrecta
        }

        # Mock de _() para asegurar respuestas en inglés durante las pruebas
        with patch('api.route.login_routes._') as mock_gettext:
            mock_gettext.return_value = 'Email or password incorrect.'
            
            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Email or password incorrect.')

    def test_login_nonexistent_user(self):
        """Dado un email que no existe en la base de datos,
        se debe recibir un código 401 y un mensaje de error adecuado.
        """
        login_data = {
            "email": "nonexistent@example.com",  # Email que no existe
            "password": "SomePassword123_"
        }

        # Mock de _() para asegurar respuestas en inglés durante las pruebas
        with patch('api.route.login_routes._') as mock_gettext:
            mock_gettext.return_value = 'Email or password incorrect.'
            
            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Email or password incorrect.')

    def test_login_subscriber_no_password(self):
        """
        Dado un email de suscriptor sin contraseña,
        se debe recibir un código 401 y un mensaje de error adecuado.
        """
        
        subscriber_email = "test_subscriber@example.com"
        users_collection.insert_one({
            "_id": ObjectId(),
            "email": subscriber_email,
            "username": subscriber_email.split("@")[0],
            "created_at": datetime.now().isoformat(),
            "role": "free",
            "email_verified": False,
            "account_status": "active",
            "password": None  # Sin contraseña
        })

        login_data = {
            "email": subscriber_email,
            "password": "AnyPassword123_"
        }

        # Mock de _() para asegurar respuestas en inglés durante las pruebas
        with patch('api.route.login_routes._') as mock_gettext:
            mock_gettext.return_value = 'Email or password incorrect.'
            
            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 401)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Email or password incorrect.')

    def test_login_missing_fields(self):
        """Dado un email o contraseña faltantes,
        se debe recibir un código 400 y un mensaje de error adecuado.
        """
        # Mock de _() para asegurar respuestas en inglés durante las pruebas
        with patch('api.route.login_routes._') as mock_gettext:
            mock_gettext.return_value = 'Invalid request data.'
            
            # Probar sin email
            login_data = {
                "password": "SomePassword123_"
            }

            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Invalid request data.')

            # Probar sin contraseña
            login_data = {
                "email": self.test_email
            }

            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'Invalid request data.')

    @patch('bcrypt.checkpw')
    def test_login_bcrypt_error(self, mock_checkpw: MagicMock):
        """Dado un error en bcrypt al verificar la contraseña,
        se debe recibir un código 500 y un mensaje de error adecuado.

        Args:
            mock_checkpw (MagicMock): Mock para la poder verificar la contraseña.
        """
        # Simular un error en bcrypt.checkpw
        mock_checkpw.side_effect = Exception("Error de bcrypt simulado")

        # Mock de _() para asegurar respuestas en inglés durante las pruebas
        with patch('api.route.login_routes._') as mock_gettext:
            mock_gettext.return_value = 'An error occurred during login. Please try again.'
            
            login_data = {
                "email": self.test_email,
                "password": self.test_password
            }

            response = self.client.post(
                '/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )

            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], 'An error occurred during login. Please try again.')

    def test_logout(self):
        """Dada una sesión activa, se debe recibir un código 200 y redirigir a la página de inicio."""
        with self.client.session_transaction() as flask_session:
            flask_session['user_id'] = str(ObjectId())
            flask_session['session_token'] = "test_session_token"
        response = self.client.get('/logout', follow_redirects=True)
        # Verificar la redirección
        self.assertEqual(response.status_code, 200)