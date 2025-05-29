from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from plans.models import Plan
from django.conf import settings
from dateutil.relativedelta import relativedelta

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
        Calcula a data de expiração com base na duração do plano, a partir do start_date.
        """
        if self.plan.duration == 'day':
            return self.start_date + timedelta(days=self.plan.duration_value)
        elif self.plan.duration == 'month':
            return self.start_date + relativedelta(months=self.plan.duration_value)
        elif self.plan.duration == 'year':
            return self.start_date + relativedelta(years=self.plan.duration_value)
        else:
            return self.start_date

    def calculate_end_date_from(self, base_date):
        """
        Calcula a data de expiração com base na duração do plano, a partir de uma data base.
        Útil para renovações e upgrades.
        """
        if self.plan.duration == 'day':
            return base_date + timedelta(days=self.plan.duration_value)
        elif self.plan.duration == 'month':
            return base_date + relativedelta(months=self.plan.duration_value)
        elif self.plan.duration == 'year':
            return base_date + relativedelta(years=self.plan.duration_value)
        else:
            return base_date

    class Meta:
        db_table = 'subscription'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"


class SubscriptionPayment(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True, blank=True)
    idempotency = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, choices=[
        ('PIX', 'PIX'),
        ('CREDIT_CARD', 'Credit Card'),
        ('DEBIT_CARD', 'Debit Card'),
        ('BOLETO', 'Boleto')
    ])
    gateway = models.CharField(
        max_length=20,
        choices=[
            ('zeroone', 'ZeroOne'),
            ('firebanking', 'Firebanking')
        ],
        default='zeroone'
    )
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

    class Meta:
        db_table = 'subscription_payment'
        ordering = ['-created_at']


class NotificationSend(models.Model):
    index = models.CharField(max_length=255, db_index=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.index} - {self.date}"

    class Meta:
        db_table = 'subscription_notification_send'
