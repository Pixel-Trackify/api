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

"""
@todo:
    - Testar com todos os gateways disponíveis
"""
class TestIntegrationRegistration(APITestCase):
    
    def setUp(self):
        try:
            self.register_url = reverse("account-create-list")
            # ajuste conforme sua rota de login
            self.login_url = reverse("login")
            # Criar usuário
            payload = {"email": email, "cpf": cpf, "name": name,
                        "password": password, "confirm_password": password}
            reg_response = self.client.post(
                self.register_url, payload, format="json")
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
            login_response = self.client.post(
                self.login_url, login_payload, format="json")
            self.assertEqual(login_response.status_code, status.HTTP_200_OK)
            self.access_token = login_response.data.get("access")
            self.uid = login_response.data.get("uid")
            # Definir cabeçalho de autorização
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Bearer {self.access_token}")
            
            self.create_url = reverse("integration-list")
        except NoReverseMatch as e:
            self.fail(f"Rota não encontrada: {str(e)}")
            print(f"Rota não encontrada: {str(e)}")
        except Exception as e:
            self.fail(f"Erro inesperado: {str(e)}")
            print(f"Erro inesperado: {str(e)}")
            
    def test_create_integration_empty_data(self):
        """
        Testa a criação de uma integração com dados vázios.
        """
        response = self.client.post(self.create_url, {}, format="json")
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
 
    def test_create_integration_invalid_name(self):
        """
        Testa a criação de uma integração com um nome de gateway inválido.
        """
        invalid_payload = {
            "gateway": "zeroonea",  # Valor inválido
            "name": "Teste"
        }
        response = self.client.post(self.create_url, invalid_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gateway", response.data)
        self.assertEqual(
            response.data["gateway"][0],
            "\"zeroonea\" não é um escolha válido."
        )
        
    def test_create_integration_html_injection(self):
        """
        Testa a criação de uma integração com injeção de código HTML no campo 'name'.
        """
        payload = {
            "gateway": gateway,
            "name": "<script>alert('XSS')</script>"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )
        
    def test_create_integration_non_ascii_name(self):
        """
        Testa a criação de um integração com o nome contendo caracteres não ASCII.
        """
        payload = {
            "gateway": gateway,
            "name": "😀"
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo só pode conter caracteres ASCII."
        )
        
    def test_create_integration_title_too_short(self):
        """
        Testa a criação de um integração com o título no limite mínimo de caracteres.
        """
        payload = {
            "name": "AAA",
            "gateway": gateway,
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo deve ter pelo menos 5 caracteres."
        )
        
    def test_create_integration_xss_attempt_in_title(self):
        """
        Testa a criação de um integração com o name contendo uma tentativa de XSS.
        """
        payload = {
            "name": "&lt;script&gt;alert(&#x27;XRSS&#x27;);&lt;/script&gt;",
            "gateway": gateway,
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "O campo não pode conter tags HTML."
        )

    def test_create_integration_name_too_long(self):
        """
        Testa a criação de uma integração com um nome maior que 200 caracteres.
        """
        long_name = "A" * 201
        payload = {
            "gateway": gateway,
            "name": long_name
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)
        self.assertEqual(
            response.data["name"][0],
            "Certifique-se de que este campo não tenha mais de 100 caracteres."
        )
    
    def test_create_integration(self):
        """
        Testa a criação de uma nova integração.
        """
        payload = {
            "gateway": gateway,
            "name": nameIntegration
        }
        response = self.client.post(self.create_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("webhook_url", response.data)
        self.assertIn("uid", response.data)
        self.assertIn("name", response.data)
        self.assertIn("gateway", response.data)
        self.assertIn("status", response.data)
        self.assertEqual(response.data["gateway"], gateway)
        self.assertEqual(response.data["name"], nameIntegration)
        self.assertTrue(UUID(response.data["uid"], version=4))
        self.assertTrue(response.data["webhook_url"].startswith("http"))
        self.assertIn(gateway.lower(), response.data["webhook_url"])
        self.assertIn(str(response.data["uid"]), response.data["webhook_url"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
