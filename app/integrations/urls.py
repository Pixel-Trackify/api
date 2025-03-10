from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationDetailView, ZeroOneWebhookView, TransactionDetailView, TransactionListView, GhostsPayWebhookView, ParadisePagWebhookView, DisruptyWebhookView, WolfPayWebhookView, VegaCheckoutWebhookView, CloudFyWebhookView

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('integration/<uuid:uid>/', IntegrationDetailView.as_view(),
         name='integration-detail'),
    path('webhook/zeroone/<str:uid>/',
         ZeroOneWebhookView.as_view(), name='zeroone-webhook'),
    path('webhook/ghostspay/<str:uid>/',
         GhostsPayWebhookView.as_view(), name='ghostspay-webhook'),
    path('webhook/paradisepag/<str:uid>/',
         ParadisePagWebhookView.as_view(), name='paradisepag-webhook'),
    path('webhook/disrupty/<str:uid>/',
         DisruptyWebhookView.as_view(), name='disrupty-webhook'),
    path('webhook/wolfpay/<str:uid>/',
         WolfPayWebhookView.as_view(), name='wolfpay-webhook'),
    path('webhook/vegacheckout/<str:uid>/',
         VegaCheckoutWebhookView.as_view(), name='vegacheckout-webhook'),
    path('webhook/cloudfy/<str:uid>/',
         CloudFyWebhookView.as_view(), name='cloudfy-webhook'),
    path('zeroone/transactions/<str:transaction_id>/',
         TransactionDetailView.as_view(), name='transaction-detail'),
    path('zeroone/transactions/', TransactionListView.as_view(),
         name='transaction-list'),


]
