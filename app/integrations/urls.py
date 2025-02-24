from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationDetailView, ZeroOneWebhookView, TransactionDetailView, TransactionListView

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('integration/<uuid:uid>/', IntegrationDetailView.as_view(),
         name='integration-detail'),
    path('webhook/zeroone/<str:uid>/',
         ZeroOneWebhookView.as_view(), name='zeroone-webhook'),
    path('transactions/<str:transaction_id>/',
         TransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]
