from django.db import models
from django.conf import settings


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
    is_current = models.BooleanField(default=False, verbose_name="active-plan")  # Indica se é o plano atual (destaque)
    description = models.TextField(blank=True, verbose_name="description-adm")  # Visível apenas no admin
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="creation-date")

    def __str__(self):
        return self.name  # Representação legível no admin


class PlanFeature(models.Model):
    """Características específicas de cada plano"""
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE,
        related_name='features',  # Acessar features via plano.features.all()
        verbose_name="related-plan"
    )
    text = models.CharField(max_length=200, verbose_name="deature-description")

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

    def __str__(self):
        # Identificação clara no admin
        return f"{self.user.email} - {self.plan.name}"
