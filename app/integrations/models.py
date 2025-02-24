from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Integration(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='integrations')
    name = models.CharField(max_length=255)
    platform = models.CharField(max_length=100, default='ZeroOne')
    credentials = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'integrations'


class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    integration = models.ForeignKey(Integration, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id

    class Meta:
        db_table = 'transactions'