import uuid
from django.db import models
from django.conf import settings
from campaigns.models import Campaign
from django.contrib.auth import get_user_model

User = get_user_model()


class Kwai(models.Model):
    user = models.ForeignKey(

        User, on_delete=models.CASCADE, null=True,
        blank=True,
    )

    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'kwai'


class KwaiCampaign(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name="kwai_campaigns")
    kwai = models.ForeignKey(
        Kwai, on_delete=models.CASCADE, related_name="campaigns")

    def __str__(self):
        return f"KwaiCampaign: {self.campaign.name} - {self.kwai.name}"

    class Meta:
        db_table = 'kwai_campaigns'
