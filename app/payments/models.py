from django.db import models
from django.conf import settings
from plans.models import Plan
import uuid


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('expired', 'Expired'),
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
    ]

    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending')
    expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'subscription'

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} - {self.status}"


class SubscriptionPayment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('pix', 'PIX'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('boleto', 'Boleto'),
    ]

    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Paid'),
    ]

    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    idempotency = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES)
    token = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    gateway_response = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)

    class Meta:
        db_table = 'subscription_payment'

    def __str__(self):
        return f"{self.uid} - {self.payment_method} - {self.status}"
