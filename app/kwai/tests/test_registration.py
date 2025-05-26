from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import UUID
from datetime import timedelta
from django.utils import timezone
from plans.models import Plan
from payments.models import UserSubscription, SubscriptionPayment
import uuid

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

class KwaiAccountTests(APITestCase):
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

            # Adicionar uma assinatura para o usuário
            user = User.objects.get(email=TEST_EMAIL)
            user.subscription_active = True
            user.subscription_expiration = timezone.now() + timedelta(days=30)
            user.save()
            
            # Crie um plano de teste
            plan = Plan.objects.create(
                name="Plano Teste",
                price=49.99,
                duration="month",
                duration_value=1,
                is_current=True,
                campaign_limit=5,
                integration_limit=5,
                kwai_limit=5,
                description="Plano de teste para integração"
            )

            # Crie uma assinatura ativa para o usuário
            subscription = UserSubscription.objects.create(
                user=user,
                plan=plan,
                start_date=timezone.now(),
                expiration=timezone.now() + timedelta(days=30),
                is_active=True,
                status="active"
            )

            # Crie um pagamento para a assinatura
            SubscriptionPayment.objects.create(
                uid=uuid.uuid4(),
                idempotency=f"{user.pk}-{plan.uid}-PIX",
                payment_method="PIX",
                gateway="zeroone",
                price=plan.price,
                status=True,
                subscription=subscription
            )

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

            # URL de contas Kwai
            self.kwai_url = reverse("kwai-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {e}")
        except Exception as e:
            self.fail(f"Erro inesperado no setUp: {e}")

    def test_create_empty_kwai_data(self):
        """
        Deve falhar ao criar conta Kwai sem nome ou campanhas.
        """
        resp = self.client.post(self.kwai_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", resp.data)
        self.assertIn("campaigns", resp.data)
        self.assertEqual(resp.data["name"][0], "Este campo é obrigatório.")
        self.assertEqual(resp.data["campaigns"][0], "Este campo é obrigatório.")

    def test_block_html_in_name(self):
        """
        Deve impedir injeção de tags HTML no nome da conta.
        """
        payload = {"name": "<script>alert('XSS')</script>",
                   "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["name"][0], "O campo não pode conter tags HTML.")

    def test_block_escaped_html(self):
        """
        Deve bloquear HTML escapado no nome da conta.
        """
        payload = {"name": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
                   "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["name"][0], "O campo não pode conter tags HTML.")

    def test_only_ascii_allowed(self):
        """
        Deve rejeitar caracteres não-ASCII no nome.
        """
        payload = {"name": "😀", "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["name"][0], "O campo só pode conter caracteres ASCII.")

    def test_name_too_short(self):
        """
        Deve rejeitar nome com menos de 5 caracteres.
        """
        payload = {"name": "A", "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["name"][0], "O campo deve ter pelo menos 5 caracteres.")

    def test_name_too_long(self):
        """
        Deve rejeitar nome com mais de 100 caracteres.
        """
        payload = {"name": "A" * 101, "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            resp.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )

    def test_invalid_campaign_uuid(self):
        """
        Deve falhar ao informar UUID inválido para campaigns.
        """
        payload = {"name": CAMPAIGN_TITLE, "campaigns": [{"uid": "not-a-uuid"}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("campaigns", resp.data)
        self.assertEqual(resp.data["campaigns"][0]['uid'][0], 'Must be a valid UUID.')

    def test_duplicate_campaign_usage(self):
        """
        Deve impedir reutilização de campanha já em uso.
        """
        # Primeiro registro
        first = {"name": "Primeiro Kwai", "campaigns": [{"uid": self.campaign_uid}]}
        resp1 = self.client.post(self.kwai_url, first, format="json")
        self.assertEqual(resp1.status_code, status.HTTP_201_CREATED)

        # Reuso de mesma campanha
        second = {"name": "Segundo Kwai", "campaigns": [{"uid": self.campaign_uid}]}
        resp2 = self.client.post(self.kwai_url, second, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp2.data["campaigns"], "A campanha já está em uso.")

    def test_successful_kwai_creation(self):
        """
        Deve criar conta Kwai quando payload for válido.
        """
        payload = {"name": "Conta Kwai Teste", "campaigns": [{"uid": self.campaign_uid}]}
        resp = self.client.post(self.kwai_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("uid", resp.data)
        self.assertIn("name", resp.data)
        self.assertIn("campaigns", resp.data)
        self.assertEqual(resp.data["name"], "Conta Kwai Teste")
        self.assertEqual(len(resp.data["campaigns"]), 1)
        self.assertEqual(resp.data["campaigns"][0]["uid"], self.campaign_uid)
