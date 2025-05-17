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
  