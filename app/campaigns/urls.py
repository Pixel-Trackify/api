from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CampaignViewSet, KwaiWebhookView

router = DefaultRouter()
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/kwai/<uuid:uid>/',
         KwaiWebhookView.as_view(), name='kwai-webhook'),
]
