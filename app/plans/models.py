from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class Plan(models.Model):
    """Modelo para representar planos de assinatura"""
    DURATION_CHOICES = [
        ('month', 'Mensal'),  # Opções de duração
        ('year', 'Anual'),
    ]

    # Campos básicos do plano
    name = models.CharField(max_length=100, unique=True,verbose_name="name-plan")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="price")
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='month', verbose_name="duration")
    duration_value = models.PositiveIntegerField(default=1, verbose_name="duration-value")  # Valor da duração
    is_current = models.BooleanField(default=False, verbose_name="active-plan")  # Indica se é o plano atual (destaque)
    description = models.TextField(blank=True, verbose_name="description-adm")  # Visível apenas no admin
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creation-date")


    class Meta:
        db_table = 'Plan'

    def __str__(self):
        return self.name  # Representação legível no admin


class PlanFeature(models.Model):
    """Características específicas de cada plano"""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE,
        related_name='features',  # Acessar features via plano.features.all()
        verbose_name="related-plan"
    )
    text = models.CharField(max_length=200, verbose_name="deature-description")

    class Meta:
        db_table = 'plan_feature'

    def __str__(self):
        return self.text  # Exibe o texto no admin


class UserSubscription(models.Model):
    """Vincula usuários a planos (histórico de assinaturas)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='subscriptions',  # Acessar via user.subscriptions.all()
        verbose_name="Usuário"
    )
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE,verbose_name="contracted-plan")
    start_date = models.DateTimeField(auto_now_add=True, verbose_name="start-date")  # Automático na criação
    end_date = models.DateTimeField(verbose_name="end-date")
    is_active = models.BooleanField(default=True, verbose_name="active-subscription")  # Pode ser desativada

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.calculate_end_date()
        super().save(*args, **kwargs)

    def calculate_end_date(self):
        if self.plan.duration == 'month':
            return self.start_date + timedelta(days=30 * self.plan.duration_value)
        elif self.plan.duration == 'year':
            return self.start_date + timedelta(days=365 * self.plan.duration_value)
        return self.start_date


    class Meta:
        db_table = 'user_subscription'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"
