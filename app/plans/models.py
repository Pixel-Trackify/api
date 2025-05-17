from django.db import models
import uuid


class Plan(models.Model):
    """Modelo para representar planos de assinatura"""
    DURATION_CHOICES = [
        ('day', 'Diário'),
        ('month', 'Mensal'),
        ('year', 'Anual'),
    ]

    # Campos básicos do plano
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="name-plan")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="price")
    duration = models.CharField(
        max_length=10, choices=DURATION_CHOICES, default='month', verbose_name="duration")
    duration_value = models.PositiveIntegerField(
        default=1, verbose_name="duration-value")  # Valor da duração
    # Indica se é o plano atual (destaque)
    is_current = models.BooleanField(default=False, verbose_name="active-plan")
    description = models.TextField(
        blank=True, verbose_name="description-adm")  # Visível apenas no admin
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="creation-date")

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
    text = models.CharField(max_length=200, verbose_name="feature-description")
    active = models.BooleanField(default=True, verbose_name="active-feature")

    class Meta:
        db_table = 'plan_feature'

    def __str__(self):
        return self.text  # Exibe o texto no admin
