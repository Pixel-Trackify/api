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

    def test_create_tutorial_invalid_html_in_title(self):
        """
        Testa a criação de um tutorial com o título contendo tags HTML inválidas (possível tentativa de XSS).
        """
        payload = {
            "title": "<script>alert('XSS')</script>",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
        
    def test_create_tutorial_non_ascii_title(self):
        """
        Testa a criação de um tutorial com o título contendo caracteres não ASCII.
        """
        payload = {
            "title": "😀",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_create_tutorial_xss_attempt_in_title(self):
        """
        Testa a criação de um tutorial com o título contendo uma tentativa de XSS.
        """
        payload = {
            "title": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
        
    def test_create_tutorial_min_description_length(self):
        """
        Testa a criação de um tutorial com a descrição no limite mínimo de caracteres.
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "AAA",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )

    def test_create_tutorial_exceed_max_description_length(self):
        """
        Testa a criação de um tutorial com a descrição excedendo o limite máximo de caracteres.
        """
        too_long_description = "A" * 501
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": too_long_description,
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode exceder 500 caracteres."
        )

    def test_create_tutorial_invalid_html_in_description(self):
        """
        Testa a criação de um tutorial com a descrição contendo tags HTML inválidas (possível tentativa de XSS).
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "<script>alert('XSS')</script>",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode conter tags HTML."
        )

    def test_create_tutorial_non_ascii_description(self):
        """
        Testa a criação de um tutorial com a descrição contendo caracteres não ASCII.
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "😀",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo só pode conter caracteres ASCII."
        )
    
class TestTutorialEditing(APITestCase):
    
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
        
            # Ajustar a rota correta para tutoriais
            self.update_url = self.create_url +  self.tutorial_id + "/"
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_update_tutorial_empty_data(self):
        """
        Testa a criação de um tutorial com dados vázios.
        """
        invalid_payload = {
            "title": "",
            "description": "",
            "youtube_url": ""
        }
        response = self.client.put(self.update_url, invalid_payload, format="json")
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
        
    def test_update_tutorial_min_title_length(self):
        """
        Testa a criação de um tutorial com o título no limite mínimo de caracteres.
        """
        payload = {
            "title": "AAA",
            "description": "Valid description",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )

    def test_update_tutorial_exceed_max_title_length(self):
        """
        Testa a criação de um tutorial com o título excedendo o limite máximo de caracteres.
        """
        too_long_title = "A" * 101
        payload = {
            "title": too_long_title,
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode exceder 100 caracteres."
        )

    def test_update_tutorial_invalid_html_in_title(self):
        """
        Testa a criação de um tutorial com o título contendo tags HTML inválidas (possível tentativa de XSS).
        """
        payload = {
            "title": "<script>alert('XSS')</script>",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
        
    def test_update_tutorial_non_ascii_title(self):
        """
        Testa a criação de um tutorial com o título contendo caracteres não ASCII.
        """
        payload = {
            "title": "😀",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_update_tutorial_xss_attempt_in_title(self):
        """
        Testa a criação de um tutorial com o título contendo uma tentativa de XSS.
        """
        payload = {
            "title": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "description": "",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(
            response.data["title"][0],
            "O campo não pode conter tags HTML."
        )
        
    def test_update_tutorial_min_description_length(self):
        """
        Testa a criação de um tutorial com a descrição no limite mínimo de caracteres.
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "AAA",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )

    def test_update_tutorial_exceed_max_description_length(self):
        """
        Testa a criação de um tutorial com a descrição excedendo o limite máximo de caracteres.
        """
        too_long_description = "A" * 501
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": too_long_description,
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode exceder 500 caracteres."
        )

    def test_update_tutorial_invalid_html_in_description(self):
        """
        Testa a criação de um tutorial com a descrição contendo tags HTML inválidas (possível tentativa de XSS).
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "<script>alert('XSS')</script>",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo não pode conter tags HTML."
        )

    def test_update_tutorial_non_ascii_description(self):
        """
        Testa a criação de um tutorial com a descrição contendo caracteres não ASCII.
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "😀",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertEqual(
            response.data["description"][0],
            "O campo só pode conter caracteres ASCII."
        )
      
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
               
class TestTutorialDeletion(APITestCase):
    
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
        
            # Ajustar a rota correta para tutoriais
            self.delete_url = self.create_url +  self.tutorial_id + "/"
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
    
    def test_delete_tutorial_invalid_uid(self):
        """
        Testa a exclusão de uma tutorial com um UID inválida.
        """
        delete_url = self.create_url + "847b4a59-5ca6-4335-bc97-b2a07e1eddc7/" 
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "No Tutorial matches the given query."
        )
            
    def test_delete_tutorial(self):
        """
        Testa a exclusão de um tutorial.
        """
        response = self.client.delete(self.delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "Tutorial excluído com sucesso."
        )
        
        # Verifica se o tutorial foi realmente deletado
        response = self.client.get(self.delete_url) # essa URL simula o detalhes do tutorial
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_delete_tutorial_not_found(self):
        """
        Testa a exclusão de um tutorial que não existe.
        """
        invalid_uid = str(UUID(int=0))
        invalid_delete_url = self.create_url + invalid_uid + "/"
        response = self.client.delete(invalid_delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
class TestTutorialBulkDeletion(APITestCase):
    
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
        
            # Ajustar a rota correta para tutoriais
            self.bulk_delete_url = reverse("tutorial-delete-multiple")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
    
    def test_bulk_delete_tutorials_invalid_uid(self):
        """
        Testa a exclusão em massa de tutoriais com um UID inválida.
        """
        payload = {
            "uids": ["847b4a59-5ca6-4335-bc97-b2a07e1eddc7"]
        }
        response = self.client.post(self.bulk_delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Nenhum tutorial encontrado."
        )       
         
    def test_bulk_delete_tutorials(self):
        """
        Testa a exclusão em massa de tutoriais.
        """
        payload = {
            "uids": [self.tutorial_id]
        }
        response = self.client.post(self.bulk_delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "1 tutorial(s) excluído(s) com sucesso."
        )
        
        # Verifica se o tutorial foi realmente deletado
        detail = self.create_url + self.tutorial_id + "/"
        response = self.client.get(detail)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
  
class TestTutorialDetailWithoutAdmin(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            
            # Criar usuário Admin
            payload = {"email": "marcos.vinicius.rezende@gmail.com", "cpf": '36835819308', "name": "Marcos Vinicius Ruan Guilherme Rezende",
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Alterar para admin diretamente no banco
            user = User.objects.get(email="marcos.vinicius.rezende@gmail.com")
            user.is_superuser = True
            user.save()

            # Autenticar para obter token
            login_payload = {"identifier": "marcos.vinicius.rezende@gmail.com", "password": password}
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
            # Cria usuário comum para o teste
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

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
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_get_tutorial_detail_as_non_admin(self):
        
        detail_url = self.create_url + self.tutorial_id + "/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestTutorialDeletionWithoutAdmin(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            
            # Criar usuário Admin
            payload = {"email": "marcos.vinicius.rezende@gmail.com", "cpf": '36835819308', "name": "Marcos Vinicius Ruan Guilherme Rezende",
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Alterar para admin diretamente no banco
            user = User.objects.get(email="marcos.vinicius.rezende@gmail.com")
            user.is_superuser = True
            user.save()

            # Autenticar para obter token
            login_payload = {"identifier": "marcos.vinicius.rezende@gmail.com", "password": password}
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
            # Cria usuário comum para o teste
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)
            # Ajustar a rota correta para tutoriais
            self.delete_url = self.create_url +  self.tutorial_id + "/"
            
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
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_delete_tutorial_as_non_admin(self):
        """
        Testa a exclusão de um tutorial sem permissões de administrador.
        """
        response = self.client.delete(self.delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class TestTutorialEditingWithoutAdmin(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            
            # Criar usuário Admin
            payload = {"email": "marcos.vinicius.rezende@gmail.com", "cpf": '36835819308', "name": "Marcos Vinicius Ruan Guilherme Rezende",
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

            # Alterar para admin diretamente no banco
            user = User.objects.get(email="marcos.vinicius.rezende@gmail.com")
            user.is_superuser = True
            user.save()

            # Autenticar para obter token
            login_payload = {"identifier": "marcos.vinicius.rezende@gmail.com", "password": password}
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
            self.edit_url = self.create_url + self.tutorial_id + "/"
            # Cria usuário comum para o teste
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)

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
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_edit_tutorial_as_non_admin(self):
        """
        Testa a edição de um tutorial sem permissões de administrador.
        """
        payload = {
            "title": "Updated Title",
            "description": "Updated description",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.put(self.edit_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
  
class TestTutorialRegistrationWithoutAdmin(APITestCase):
    
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

            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(
                self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
            # Ajustar a rota correta para tutoriais
            self.create_url = reverse("tutorial-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")

    def test_create_tutorial_as_non_admin(self):
        """
        Testa a criação de um tutorial sem permissões de administrador.
        """
        payload = {
            "title": "Como criar uma campanha do Kwai",
            "description": "Alguma descrição válida",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)