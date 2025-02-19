from django.db import models
import uuid


class Campaign(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    source = models.CharField(max_length=100, default='Kwai')
    title = models.CharField(max_length=255)
    CPM = models.DecimalField(max_digits=10, decimal_places=2)
    total_approved = models.IntegerField(default=0)
    total_pending = models.IntegerField(default=0)
    amount_approved = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    amount_pending = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    total_ads = models.IntegerField(default=0)
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ROI = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_views = models.IntegerField(default=0)
    total_clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CampaignView(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='views')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    action = models.CharField(max_length=10)  # 'view' ou 'click'

    def __str__(self):
        return f"{self.campaign.title} - {self.action} - {self.created_at}"
