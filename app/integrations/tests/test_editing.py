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
email = "tester@gmail.com"
cpf = "63861694921"
name = "Sarah Isabela Lima"
password = "7lonAzJxss@"

gateway = "zeroone"
nameIntegration = "Conta da Sarah - ZeroOne"

class TestIntegrationUpdate(APITestCase):
    
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

            # Adicionar uma assinatura para o usuário
            user = User.objects.get(email=email)
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
            
            # Autenticar para obter token
            login_payload = {"identifier": email, "password": password}
            login_response = self.client.post(self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            # Criar uma integração para atualizar
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            create_response = self.client.post(self.create_url, integration_payload, format="json")
            self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
            self.integration_uid = create_response.data["uid"]
            self.update_url = reverse("integration-list") + self.integration_uid + "/" 
        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_update_integration_empty_data(self):
        """
        Testa a atualização de uma integração com dados vázios.
        """
        response = self.client.put(self.update_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gateway", response.data)   
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["gateway"][0],
            "Este campo é obrigatório."
        )
        self.assertEqual(
            response.data["name"][0],
            "Este campo é obrigatório."
        )
 
    def test_update_integration_invalid_name(self):
        """
        Testa a atualização de uma integração com um nome de gateway inválido.
        """
        invalid_payload = {
            "gateway": "zeroonea",
            "name": "Teste Atualizado"
        }
        response = self.client.put(self.update_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gateway", response.data)
        self.assertEqual(
            response.data["gateway"][0],
            "\"zeroonea\" não é um escolha válido."
        )

    def test_update_integration_html_injection(self):
        """
        Testa a atualização de uma integração com injeção de código HTML no campo 'name'.
        """
        payload = {
            "gateway": gateway,
            "name": "<script>alert('XSS')</script>"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )

    def test_update_integration_non_ascii_name(self):
        """
        Testa a atualização de um integração com o nome contendo caracteres não ASCII.
        """
        payload = {
            "gateway": gateway,
            "name": "😀"
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_update_integration_title_too_short(self):
        """
        Testa a atualização de um integração com o título no limite mínimo de caracteres.
        """
        payload = {
            "name": "AAA",
            "gateway": gateway,
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )
        
    def test_update_integration_xss_attempt_in_title(self):
        """
        Testa a atualização de um integração com o name contendo uma tentativa de XSS.
        """
        payload = {
            "name": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "gateway": gateway,
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )

    def test_update_integration_name_too_long(self):
        """
        Testa a atualização de uma integração com um nome maior que 200 caracteres.
        """
        long_name = "A" * 201
        payload = {
            "gateway": gateway,
            "name": long_name
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )

    def test_update_integration(self):
        """
        Testa a atualização de uma integração com dados válidos.
        """
        updated_name = "Conta Atualizada - ZeroOne"
        payload = {
            "gateway": gateway,
            "name": updated_name
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], updated_name)
        self.assertEqual(response.data["gateway"], gateway)
