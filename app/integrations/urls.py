from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationDetailView, ZeroOneWebhookView, TransactionDetailView, TransactionListView, PagFlexWebhookView

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('integration/<uuid:uid>/', IntegrationDetailView.as_view(),
         name='integration-detail'),
    path('webhook/zeroone/<str:uid>/',
         ZeroOneWebhookView.as_view(), name='zeroone-webhook'),
    path('webhook/pagflex/<str:uid>/',
         PagFlexWebhookView.as_view(), name='pagflex-webhook'),
    path('zeroone/transactions/<str:transaction_id>/',
         TransactionDetailView.as_view(), name='transaction-detail'),
    path('zeroone/transactions/', TransactionListView.as_view(),
         name='transaction-list'),
]
