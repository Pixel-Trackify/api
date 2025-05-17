from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID

User = get_user_model()

# Dados de exemplo para criação de usuário
email = "tester@gmail.com"
cpf = "63861694921"
name = "Sarah Isabela Lima"
password = "7lonAzJxss@"

class TestTutorialListing(APITestCase):
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            self.create_url = reverse("tutorial-list")

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

            # Criar três tutoriais reais para listar e testar filtro
            self.tutorials = [
                {
                    "title": "Introdução ao Django ORM",
                    "description": "Aprenda a usar o ORM do Django para realizar operações de banco de dados de forma simples.",
                    "youtube_url": "https://www.youtube.com/watch?v=Z1RJmh_OqeA"
                },
                {
                    "title": "Consumindo APIs com Django REST Framework",
                    "description": "Veja como construir e consumir APIs REST usando Django REST Framework e Postman.",
                    "youtube_url": "https://www.youtube.com/watch?v=GMppyAPbLYk"
                },
                {
                    "title": "Deploy de Aplicações Django na AWS",
                    "description": "Passo a passo para realizar deploy de um projeto Django usando Elastic Beanstalk.",
                    "youtube_url": "https://www.youtube.com/watch?v=3Oh4it4wC8I"
                }
            ]
            for tut in self.tutorials:
                self.client.post(self.create_url, tut, format="json")
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_list_tutorials(self):
        """
        Testa a listagem de tutoriais cadastrados.
        """
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        self.assertEqual(len(response.data["results"]), 3)

    def test_filter_by_title(self):
        """
        Testa a listagem filtrada pelo título.
        """
        response = self.client.get(f"{self.create_url}?search=Django ORM")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], "Introdução ao Django ORM")

    def test_filter_by_description(self):
        """
        Testa a listagem filtrada pela descrição.
        """
        response = self.client.get(f"{self.create_url}?search=Postman")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], "Consumindo APIs com Django REST Framework")

    def test_filter_by_youtube_url(self):
        """
        Testa a listagem filtrada pelo ID do vídeo no YouTube.
        """
        # Pesquisa pelo ID '3Oh4it4wC8I' presente na URL
        response = self.client.get(f"{self.create_url}?search=3Oh4it4wC8I")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["title"], "Deploy de Aplicações Django na AWS")
        self.assertIn(result["youtube_url"], "https://www.youtube.com/watch?v=3Oh4it4wC8I")
               