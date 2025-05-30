from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from rest_framework import status
from rest_framework.test import APITestCase
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

namecampaign = "Campanha APP da Sara"
descriptionCampaign = "Campanha de teste para o APP da Sara"
methodCampaign = "CPC"
amountCampaign = 4.25

class testCampaignDeleteFromAnotherUser(APITestCase):
    
    def setUp(self):
        try:
            # Criar o primeiro usuário
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            payload_user1 = {"email": email, "cpf": cpf, "name": name,
                             "password": password, "confirm_password": password}
            reg_response_user1 = self.client.post(self.register_url, payload_user1, format="json")
            self.assertEqual(reg_response_user1.status_code, status.HTTP_201_CREATED)

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
            
            # Autenticar o primeiro usuário
            login_payload_user1 = {"identifier": email, "password": password}
            login_response_user1 = self.client.post(self.login_url, login_payload_user1, format="json")
            self.assertEqual(login_response_user1.status_code, status.HTTP_200_OK)
            self.access_token_user1 = login_response_user1.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user1}")

            # Criar integração e campanha para o primeiro usuário
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration_user1 = integration_response.data.get("uid")

            campaign_payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration_user1],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            campaign_response = self.client.post(reverse("campaign-list"), campaign_payload, format="json")
            self.assertEqual(campaign_response.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_user1 = campaign_response.data.get("uid")

            # Criar o segundo usuário
            payload_user2 = {"email": "user2@gmail.com", "cpf": "52641983303", "name": "User Two",
                             "password": password, "confirm_password": password}
            reg_response_user2 = self.client.post(self.register_url, payload_user2, format="json")
            self.assertEqual(reg_response_user2.status_code, status.HTTP_201_CREATED)

            # Autenticar o segundo usuário
            login_payload_user2 = {"identifier": "user2@gmail.com", "password": password}
            login_response_user2 = self.client.post(self.login_url, login_payload_user2, format="json")
            self.assertEqual(login_response_user2.status_code, status.HTTP_200_OK)
            self.access_token_user2 = login_response_user2.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user2}")

            # Definir a URL de exclusão para a campanha do primeiro usuário
            self.delete_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid_user1})

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_delete_other_user_campaign(self):
        """
        Testa se um usuário pode excluir a campanha de outro usuário.
        """
        response = self.client.delete(self.delete_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
class testCampaignBulkDeleteFromAnotherUser(APITestCase):
    
    def setUp(self):
        try:
            # Criar o primeiro usuário
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            payload_user1 = {"email": email, "cpf": cpf, "name": name,
                             "password": password, "confirm_password": password}
            reg_response_user1 = self.client.post(self.register_url, payload_user1, format="json")
            self.assertEqual(reg_response_user1.status_code, status.HTTP_201_CREATED)
            
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
            
            # Autenticar o primeiro usuário
            login_payload_user1 = {"identifier": email, "password": password}
            login_response_user1 = self.client.post(self.login_url, login_payload_user1, format="json")
            self.assertEqual(login_response_user1.status_code, status.HTTP_200_OK)
            self.access_token_user1 = login_response_user1.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user1}")

            # Criar integração e campanha para o primeiro usuário
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration_user1 = integration_response.data.get("uid")

            campaign_payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration_user1],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            campaign_response = self.client.post(reverse("campaign-list"), campaign_payload, format="json")
            self.assertEqual(campaign_response.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_user1 = campaign_response.data.get("uid")

            # Criar o segundo usuário
            payload_user2 = {"email": "user2@gmail.com", "cpf": "52641983303", "name": "User Two",
                             "password": password, "confirm_password": password}
            reg_response_user2 = self.client.post(self.register_url, payload_user2, format="json")
            self.assertEqual(reg_response_user2.status_code, status.HTTP_201_CREATED)

            # Autenticar o segundo usuário
            login_payload_user2 = {"identifier": "user2@gmail.com", "password": password}
            login_response_user2 = self.client.post(self.login_url, login_payload_user2, format="json")
            self.assertEqual(login_response_user2.status_code, status.HTTP_200_OK)
            self.access_token_user2 = login_response_user2.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user2}")

            # Definir a URL de exclusão para a campanha do primeiro usuário
            self.delete_url = reverse("campaign-delete-multiple")
            self.payload = {"uids": [self.campaign_uid_user1]}

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")

    def test_bulk_delete_other_user_campaign(self):
        """
        Testa se um usuário pode excluir a campanha de outro usuário.
        """
        response = self.client.post(self.delete_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
class testCampaignEditFromAnotherUser(APITestCase):
    
    def setUp(self):
        try:
            # Criar o primeiro usuário
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            payload_user1 = {"email": email, "cpf": cpf, "name": name,
                             "password": password, "confirm_password": password}
            reg_response_user1 = self.client.post(self.register_url, payload_user1, format="json")
            self.assertEqual(reg_response_user1.status_code, status.HTTP_201_CREATED)

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
            
            # Autenticar o primeiro usuário
            login_payload_user1 = {"identifier": email, "password": password}
            login_response_user1 = self.client.post(self.login_url, login_payload_user1, format="json")
            self.assertEqual(login_response_user1.status_code, status.HTTP_200_OK)
            self.access_token_user1 = login_response_user1.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user1}")

            # Criar integração e campanha para o primeiro usuário
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration_user1 = integration_response.data.get("uid")

            campaign_payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration_user1],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            campaign_response = self.client.post(reverse("campaign-list"), campaign_payload, format="json")
            self.assertEqual(campaign_response.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_user1 = campaign_response.data.get("uid")

            # Criar o segundo usuário
            payload_user2 = {"email": "user2@gmail.com", "cpf": "52641983303", "name": "User Two",
                             "password": password, "confirm_password": password}
            reg_response_user2 = self.client.post(self.register_url, payload_user2, format="json")
            self.assertEqual(reg_response_user2.status_code, status.HTTP_201_CREATED)

            # Autenticar o segundo usuário
            login_payload_user2 = {"identifier": "user2@gmail.com", "password": password}
            login_response_user2 = self.client.post(self.login_url, login_payload_user2, format="json")
            self.assertEqual(login_response_user2.status_code, status.HTTP_200_OK)
            self.access_token_user2 = login_response_user2.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user2}")

            # Definir a URL de exclusão para a campanha do primeiro usuário
            self.update_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid_user1})

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")
            
    def test_edit_other_user_campaign(self):
        """
        Testa se um usuário pode editar a campanha de outro usuário.
        """
        payload = {
            "title": "Campanha Editada",
            "description": "Descrição editada",
            "method": "CPV",
            "CPV": 5.50
        }
        response = self.client.put(self.update_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class testCampaignDetailFromAnotherUser(APITestCase):
    
    def setUp(self):
        try:
            # Criar o primeiro usuário
            self.register_url = reverse("account-create-list")
            self.login_url = reverse("login")
            payload_user1 = {"email": email, "cpf": cpf, "name": name,
                             "password": password, "confirm_password": password}
            reg_response_user1 = self.client.post(self.register_url, payload_user1, format="json")
            self.assertEqual(reg_response_user1.status_code, status.HTTP_201_CREATED)

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
            
            # Autenticar o primeiro usuário
            login_payload_user1 = {"identifier": email, "password": password}
            login_response_user1 = self.client.post(self.login_url, login_payload_user1, format="json")
            self.assertEqual(login_response_user1.status_code, status.HTTP_200_OK)
            self.access_token_user1 = login_response_user1.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user1}")

            # Criar integração e campanha para o primeiro usuário
            integration_payload = {"gateway": gateway, "name": nameIntegration}
            integration_response = self.client.post(reverse("integration-list"), integration_payload, format="json")
            self.assertEqual(integration_response.status_code, status.HTTP_201_CREATED)
            self.uid_integration_user1 = integration_response.data.get("uid")

            campaign_payload = {
                "title": namecampaign,
                "description": descriptionCampaign,
                "integrations": [self.uid_integration_user1],
                "method": methodCampaign,
                "CPC": amountCampaign
            }
            campaign_response = self.client.post(reverse("campaign-list"), campaign_payload, format="json")
            self.assertEqual(campaign_response.status_code, status.HTTP_201_CREATED)
            self.campaign_uid_user1 = campaign_response.data.get("uid")

            # Criar o segundo usuário
            payload_user2 = {"email": "user2@gmail.com", "cpf": "52641983303", "name": "User Two",
                             "password": password, "confirm_password": password}
            reg_response_user2 = self.client.post(self.register_url, payload_user2, format="json")
            self.assertEqual(reg_response_user2.status_code, status.HTTP_201_CREATED)

            # Autenticar o segundo usuário
            login_payload_user2 = {"identifier": "user2@gmail.com", "password": password}
            login_response_user2 = self.client.post(self.login_url, login_payload_user2, format="json")
            self.assertEqual(login_response_user2.status_code, status.HTTP_200_OK)
            self.access_token_user2 = login_response_user2.data.get("access")
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token_user2}")

            # Definir a URL de exclusão para a campanha do primeiro usuário
            self.update_url = reverse("campaign-detail", kwargs={"uid": self.campaign_uid_user1})

        except Exception as e:
            self.fail(f"Erro inesperado no setup: {str(e)}")
   
    def test_detail_other_user_campaign(self):
        """
        Testa se um usuário pode acessar os detalhes da campanha de outro usuário.
        """
        response = self.client.get(self.update_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)