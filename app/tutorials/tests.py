from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID
import os

User = get_user_model()

# Dados de exemplo para criação de usuário
email = "tester@gmail.com"
cpf = "63861694921"
name = "Sarah Isabela Lima"
password = "7lonAzJxss@"

class TestTutorialRegistration(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Alterar para admin diretamente no banco
            user = User.objects.get(email=email)
            user.is_superuser = True
            user.save()

            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(
                self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.uid = login_response.data.get("uid")
            
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
            # Ajustar a rota correta para tutoriais
            self.create_url = reverse("tutorial-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_create_tutorial_empty_data(self):
        """
        Testa a criação de um tutorial com dados vázios.
        """
        invalid_payload = {
            "title": "",
            "description": "",
            "youtube_url": ""
        }
        response = self.client.post(self.create_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertIn("youtube_url", response.data)
        self.assertEqual(
            response.data["youtube_url"][0],
            "Este campo não pode ser em branco."
        ) 
        self.assertEqual(
            response.data["title"][0],
            "Este campo não pode ser em branco."
        )
        
    def test_create_tutorial_min_title_length(self):
        """
        Testa a criação de um tutorial com o título no limite mínimo de caracteres.
        """
        payload = {
            "title": "AAA",
            "description": "Valid description",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )

    def test_create_tutorial_exceed_max_title_length(self):
        """
        Testa a criação de um tutorial com o título excedendo o limite máximo de caracteres.
        """
        too_long_title = "A" * 101
        payload = {
            "title": too_long_title,
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode exceder 100 caracteres."
        )
