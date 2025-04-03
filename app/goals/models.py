import uuid
from django.db import models


class Goal(models.Model):
    id = models.BigAutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    prize = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    image = models.URLField(max_length=500, null=True, blank=True)
    min = models.FloatField()
    max = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.prize

    class Meta:
        db_table = 'goals'
