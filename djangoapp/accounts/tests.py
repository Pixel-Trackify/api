from django.urls import reverse
from rest_framework.test import APITestCase

class UsuarioAPITestCase(APITestCase):
    
    def test_usuario_cpf_invalido(self):
        """Falha ao cadastrar um usuário com CPF inválido"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@example.com",
            "cpf": "12345678901",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de CPF inválido!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_usuario_provedor_email_invalido(self):
        """Falha ao cadastrar um usuário com provedor de email invalido"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_usuario_senhas_diferentes(self):
        """Falha ao cadastrar um usuário com senhas diferentes"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@1234"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
    
    def test_usuario_senha_fraca(self):
        """Falha ao cadastrar um usuário com senha fraca"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@dominioquenaoexiste.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "123",
            "confirm_password": "123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 400)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
        
    def test_registro_usuario(self):
        """Testa a criação de um novo usuário via API"""
        url = reverse("account-create-list")
        data = {
            "email": "apiuser@gmail.com",
            "cpf": "98765432100",
            "name": "API User",
            "password": "SenhaForte@123",
            "confirm_password": "SenhaForte@123"
        }
        
        try:
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 201)
        except Exception as e:
            print("Erro no teste de registro de usuário!")
            print("Status Code:", response.status_code if 'response' in locals() else "N/A")
            print("Response Data:", response.data if 'response' in locals() else "N/A")
            print("Exceção:", str(e))
            raise
