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


class TestTutorialDetail(APITestCase):
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
            
            valid_payload = {
                "title": "Valid Title",
                "description": "Valid description",
                "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
            self.create_url = reverse("tutorial-list")
            
            create_resp = self.client.post(reverse("tutorial-list"), valid_payload, format="json")
            self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
            self.tutorial_id = create_resp.data.get("uid")
        
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            
    def test_get_tutorial_detail(self):
        """
        Testa a obtenção dos detalhes de um tutorial.
        """
        detail_url = self.create_url + self.tutorial_id + "/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("uid", response.data)
        self.assertEqual(response.data["uid"], str(self.tutorial_id))
        self.assertIn("title", response.data)
        self.assertEqual(response.data["title"], "Valid Title")
        self.assertIn("description", response.data)
        self.assertEqual(response.data["description"], "Valid description")
        self.assertIn("youtube_url", response.data)
        self.assertEqual(
            response.data["youtube_url"],
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        
    def test_get_tutorial_detail_not_found(self):
        """
        Testa a obtenção dos detalhes de um tutorial que não existe.
        """
        invalid_uid = str(UUID(int=0))
        detail_url = self.create_url + invalid_uid + "/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "No Tutorial matches the given query."
        ) 
