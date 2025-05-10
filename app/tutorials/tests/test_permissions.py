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
        
class TestTutorialBulkDeletionWithoutAdmin(APITestCase):
    
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
            self.bulk_delete_url = reverse("tutorial-delete-multiple")
            
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            
    def test_bulk_delete_tutorials_as_non_admin(self):
        """
        Testa a exclusão em massa de tutoriais sem permissões de administrador.
        """
        payload = {
            "uids": [self.uid]
        }
        response = self.client.post(self.bulk_delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)