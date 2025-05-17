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

gateway = "zeroone"
nameIntegration = "Conta da Sarah - ZeroOne"

   
class TestIntegrationBulkDeletion(APITestCase):
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            self.create_url = reverse("integration-list")
            
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                       "password": password, "confirm_password": password}
            reg_response = self.client.post(self.register_url, payload, format="json")
            self.assertEqual(reg_response.status_code, status.HTTP_201_CREATED)
            
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
            # Criar uma integração para deletar
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            create_response = self.client.post(self.create_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.assertFalse(create_response.data["deleted"])
            
            self.integration_uid = create_response.data["uid"]
            self.payload = {"uids": [self.integration_uid]}
            self.delete_url = reverse("integration-delete-multiple")
            self.detail_url = reverse("integration-list") + self.integration_uid + "/"
            
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")
            
    def test_bulk_delete_integrations_invalid_uid(self):
        """
        Testa a exclusão em massa de integrações com um UID inválida.
        """
        payload = {
            "uids": ["847b4a59-5ca6-4335-bc97-b2a07e1eddc7"]
        }
        response = self.client.post(self.delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Nenhuma integração encontrada para os UUIDs fornecidos."
        )       
         
    def test_bulk_delete_integrations(self):
        """
        Testa a exclusão em massa de integrações.
        """
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertEqual(
            response.data["message"],
            "1 integração(ões) excluída(s) com sucesso."
        )
        
        # Verifica se o tutorial foi realmente deletado
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
  