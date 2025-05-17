from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID

User = get_user_model()

# Dados de exemplo para criação de usuário
TEST_EMAIL = "tester@gmail.com"
TEST_CPF = "63861694921"
TEST_NAME = "Sarah Isabela Lima"
TEST_PASSWORD = "7lonAzJxss@"

INTEGRATION_GATEWAY = "zeroone"
INTEGRATION_NAME = "Conta da Sarah - ZeroOne"

CAMPAIGN_TITLE = "Campanha APP da Sara"
CAMPAIGN_DESCRIPTION = "Campanha de teste para o APP da Sara"
CAMPAIGN_METHOD = "CPC"
CAMPAIGN_AMOUNT = 4.25

KWAI_ACCOUNT_NAME = "Conta da Sarah - Kwai"

class KwaiAccountBulkDeleteTests(APITestCase):
    
    """
    Testes de integração para endpoints de criação e validação de contas Kwai.
    """
    def setUp(self):
        try:
            # URLs principais
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")

            # Criação de usuário
            user_payload = {
                "email": TEST_EMAIL,
                "cpf": TEST_CPF,
                "name": TEST_NAME,
                "password": TEST_PASSWORD,
                "confirm_password": TEST_PASSWORD,
            }
            reg_resp = self.client.post(self.register_url, user_payload, format="json")
            self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)

            # Autenticação
            auth_payload = {"identifier": TEST_EMAIL, "password": TEST_PASSWORD}
            auth_resp = self.client.post(self.login_url, auth_payload, format="json")
            self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
            token = auth_resp.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

            # Criação de integração
            self.integration_url = reverse("integration-list")
            integration_payload = {"gateway": INTEGRATION_GATEWAY, "name": INTEGRATION_NAME}
            int_resp = self.client.post(self.integration_url, integration_payload, format="json")
            self.assertEqual(int_resp.status_code, status.HTTP_201_CREATED)
            self.integration_uid = int_resp.data.get("uid")

            # Criação de campanha
            self.campaign_url = reverse("campaign-list")
            campaign_payload = {
                "title": CAMPAIGN_TITLE,
                "description": CAMPAIGN_DESCRIPTION,
                "integrations": [self.integration_uid],
                "method": CAMPAIGN_METHOD,
                "CPC": CAMPAIGN_AMOUNT
            }
            camp_resp = self.client.post(self.campaign_url, campaign_payload, format="json")
            self.assertEqual(camp_resp.status_code, status.HTTP_201_CREATED)
            self.campaign_uid = camp_resp.data.get("uid")     
                   
            # Criação de conta Kwai para deletar
            self.kwai_url = reverse("kwai-list")
            kwai_payload = {"name": KWAI_ACCOUNT_NAME, "campaigns": [{"uid": self.campaign_uid}]}
            kwai_resp = self.client.post(self.kwai_url, kwai_payload, format="json")
            self.assertEqual(kwai_resp.status_code, status.HTTP_201_CREATED)
            self.kwai_uid = kwai_resp.data.get("uid")
            
            self.delete_url = reverse("kwai-delete-multiple")
            self.detail_url = reverse("kwai-detail", kwargs={"uid": self.kwai_uid})
            self.payload = {"uids": [self.kwai_uid]}
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no setUp: {e}")
       
    def test_bulk_delete_invalid_uid(self):
        """
        Testa a exclusão em massa de contas kwai com um UID inválido.
        """
        payload = {
            "uids": ["847b4a59-5ca6-4335-bc97-b2a07e1eddc7"]
        }
        response = self.client.post(self.delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Alguns UIDs são inválidos ou não encontrados."
        )       
       
    def test_bulk_delete_empty_uid(self):
        """
        Testa a exclusão em massa de contas kwai com um UID vázio.
        """
        payload = {
            "uids": []
        }
        response = self.client.post(self.delete_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Nenhum UUID fornecido ou formato inválido."
        )       

    def test_bulk_delete_other_user_account(self):
        """
        Testa a tentativa de exclusão de uma conta Kwai pertencente a outro usuário.
        """
        # Criação de outro usuário
        other_user_payload = {
            "email": "seconduser@gmail.com",
            "cpf": "52641983303",
            "name": "João da Silva",
            "password": TEST_PASSWORD,
            "confirm_password": TEST_PASSWORD,
        }
        reg_resp = self.client.post(self.register_url, other_user_payload, format="json")
        self.assertEqual(reg_resp.status_code, status.HTTP_201_CREATED)

        # Autenticação do outro usuário
        auth_payload = {"identifier": "seconduser@gmail.com", "password": TEST_PASSWORD}
        auth_resp = self.client.post(self.login_url, auth_payload, format="json")
        self.assertEqual(auth_resp.status_code, status.HTTP_200_OK)
        token = auth_resp.data.get("access")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Tentativa de exclusão da conta Kwai do primeiro usuário
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "Alguns UIDs são inválidos ou não encontrados."
        )
        
    def test_bulk_delete(self):
        """
        Testa a exclusão em massa da conta Kwai.
        """
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response.data)
        self.assertEqual(
            response.data["detail"],
            "Contas Kwai excluídas com sucesso."
        )

        # Verifica se a campanha foi realmente deletada
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

