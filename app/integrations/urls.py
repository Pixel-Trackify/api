from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationDetailView, ZeroOneWebhookView, GhostsPayWebhookView, ParadisePagWebhookView, DisruptyWebhookView, WolfPayWebhookView, VegaCheckoutWebhookView, CloudFyWebhookView, TriboPayWebhookView, WestPayWebhookView, AvailableGatewaysView

router = DefaultRouter()
router.register(r'integrations-user', IntegrationViewSet,
                basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('integration/<uuid:uid>/', IntegrationDetailView.as_view(),
         name='integration-detail'),
    path('integrations/gateways/', AvailableGatewaysView.as_view(),
         name='available-gateways'),
    path('webhook/zeroone/<uuid:uid>/',
         ZeroOneWebhookView.as_view(), name='zeroone-webhook'),
    path('webhook/ghostspay/<uuid:uid>/',
         GhostsPayWebhookView.as_view(), name='ghostspay-webhook'),
    path('webhook/paradisepag/<uuid:uid>/',
         ParadisePagWebhookView.as_view(), name='paradisepag-webhook'),
    path('webhook/disrupty/<uuid:uid>/',
         DisruptyWebhookView.as_view(), name='disrupty-webhook'),
    path('webhook/wolfpay/<uuid:uid>/',
         WolfPayWebhookView.as_view(), name='wolfpay-webhook'),
    path('webhook/vegacheckout/<uuid:uid>/',
         VegaCheckoutWebhookView.as_view(), name='vegacheckout-webhook'),
    path('webhook/cloudfy/<uuid:uid>/',
         CloudFyWebhookView.as_view(), name='cloudfy-webhook'),
    path('webhook/tribopay/<uuid:uid>/',
         TriboPayWebhookView.as_view(), name='tribopay-webhook'),
    path('webhook/westpay/<uuid:uid>/',
         WestPayWebhookView.as_view(), name='westpay-webhook'),
]
