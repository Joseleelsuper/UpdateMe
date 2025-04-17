import unittest
from unittest.mock import patch
from conftest import TestBase
import json
from bson import ObjectId
from api.database import users_collection


class TestSubscription(TestBase):
    """Pruebas para la funcionalidad de suscripción por email."""

    def setUp(self):
        super().setUp()
        # Limpiamos cualquier usuario de test que pueda existir antes de cada prueba
        users_collection.delete_many({"email": {"$regex": "test.*@example.com"}})

    def tearDown(self):
        super().tearDown()
        # Limpiamos usuarios de test después de cada prueba
        users_collection.delete_many({"email": {"$regex": "test.*@example.com"}})

    @patch('resend.Emails.send')
    def test_valid_email_subscription(self, mock_send_email):
        """
        GIVEN un email válido que no existe en la base de datos
        WHEN se envía una solicitud POST a /subscribe
        THEN se debe recibir una respuesta 200 OK, el usuario debe ser guardado
             en la base de datos y se deben enviar dos correos (bienvenida y resumen)
        """
        # Configurar el mock para simular envío exitoso
        mock_send_email.return_value = {"id": "123456", "status": "success"}

        # Enviar solicitud de suscripción
        response = self.client.post(
            '/subscribe',
            data=json.dumps({"email": "test_valid@example.com"}),
            content_type='application/json'
        )

        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

        # Verificar que el usuario está en la base de datos
        user = users_collection.find_one({"email": "test_valid@example.com"})
        self.assertIsNotNone(user)

        # Verificar que se llamó a la función de enviar correo dos veces
        self.assertEqual(mock_send_email.call_count, 2)
        
        # Verificar que el primer correo es de bienvenida
        first_call = mock_send_email.call_args_list[0]
        self.assertTrue(
            '¡Bienvenido a UpdateMe!' in str(first_call) or 'Welcome to UpdateMe!' in str(first_call)
        )
        
        # Verificar que el segundo correo es el resumen semanal
        second_call = mock_send_email.call_args_list[1]
        self.assertTrue(
            'Tu resumen semanal' in str(second_call) or 'Your weekly summary' in str(second_call)
        )

    @patch('resend.Emails.send')
    def test_invalid_email_format(self, mock_send_email):
        """
        GIVEN un email con formato inválido
        WHEN se envía una solicitud POST a /subscribe
        THEN se debe recibir un código 400 y el usuario no debe guardarse
        """
        # Enviar solicitud con email inválido
        response = self.client.post(
            '/subscribe',
            data=json.dumps({"email": "invalid-email"}),
            content_type='application/json'
        )

        # Verificar respuesta
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que no se guardó en la base de datos
        user = users_collection.find_one({"email": "invalid-email"})
        self.assertIsNone(user)

        # Verificar que no se llamó a la función de enviar correo
        mock_send_email.assert_not_called()

    @patch('resend.Emails.send')
    def test_duplicate_email(self, mock_send_email):
        """
        GIVEN un email que ya existe en la base de datos
        WHEN se envía una solicitud POST a /subscribe
        THEN se debe recibir un código 409 y no se debe enviar correo
        """
        # Crear usuario de prueba primero
        test_email = "test_duplicate@example.com"
        users_collection.insert_one({
            "_id": ObjectId(),
            "email": test_email,
            "username": "testuser",
            "created_at": "2025-04-15T00:00:00",
            "role": "free",
            "email_verified": False,
            "account_status": "active"
        })

        # Intentar suscribir el mismo email
        response = self.client.post(
            '/subscribe',
            data=json.dumps({"email": test_email}),
            content_type='application/json'
        )

        # Verificar respuesta
        self.assertEqual(response.status_code, 409)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn("ya está suscrito", data['message'])

        # Verificar que no se llamó a la función de enviar correo
        mock_send_email.assert_not_called()

    @patch('resend.Emails.send')
    def test_email_sending_failure(self, mock_send_email):
        """
        GIVEN un email válido
        WHEN el servicio de envío de correo falla
        THEN se debe recibir un código 500 y el usuario no debe guardarse
        """
        # Configurar el mock para simular un error de envío
        mock_send_email.side_effect = Exception("Error de envío simulado")

        # Enviar solicitud de suscripción
        response = self.client.post(
            '/subscribe',
            data=json.dumps({"email": "test_email_fail@example.com"}),
            content_type='application/json'
        )

        # Verificar respuesta
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])

        # Verificar que el usuario NO está en la base de datos
        user = users_collection.find_one({"email": "test_email_fail@example.com"})
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()