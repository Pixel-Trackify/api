from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from plans.models import Plan
from django.conf import settings

import uuid


class UserSubscription(models.Model):
    """Vincula usuários a planos (histórico de assinaturas)"""
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='subscriptions',
                             verbose_name="Usuário"
                             )

    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, verbose_name="contracted-plan")
    start_date = models.DateTimeField(
        auto_now_add=True, verbose_name="start-date")
    expiration = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(

        default=False, verbose_name="active-subscription")
    status = models.CharField(
        max_length=20,
        choices=[
            ('expired', 'Expired'),
            ('active', 'Active'),
            ('pending', 'Pending'),
            ('canceled', 'Canceled')
        ],
        default='pending'
    )

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para calcular a data de expiração e atualizar o status.
        """

        if self.pk:
            has_paid_payment = self.payments.filter(status=True).exists()

            if has_paid_payment:
                self.is_active = True
                self.status = 'active'
            else:
                self.is_active = False
                self.status = 'pending'

        super().save(*args, **kwargs)

    def calculate_end_date(self):
        """
        Calcula a data de expiração com base na duração do plano.
        """
        if self.plan.duration == 'day':
            return self.start_date + timedelta(days=self.plan.duration_value)
        if self.plan.duration == 'month':
            return self.start_date + timedelta(days=30 * self.plan.duration_value)
        elif self.plan.duration == 'year':
            return self.start_date + timedelta(days=365 * self.plan.duration_value)
        else:
            return self.start_date

    class Meta:
        db_table = 'user_subscription'
        verbose_name = "User Subscription"
        verbose_name_plural = "User Subscriptions"

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"


class SubscriptionPayment(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    idempotency = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('PIX', 'PIX'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BOLETO', 'Boleto')
    ])
    token = models.CharField(max_length=255, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_response = models.JSONField(null=True, blank=True)
    status = models.BooleanField(default=False)
    subscription = models.ForeignKey(
        UserSubscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.uid} - {'Paid' if self.status else 'Not Paid'}"

    class meta:
        db_table = 'subscriptions_payments_zeroone'
