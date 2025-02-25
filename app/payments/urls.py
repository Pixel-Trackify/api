from django.urls import path
from .views import CreatePaymentView, PaymentStatusView, PaymentWebhookView

urlpatterns = [
    path('payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment/<uuid:uid>/', PaymentStatusView.as_view(), name='payment_status'),
    path('webhook/<str:gateway_name>/', PaymentWebhookView.as_view(), name='payment_webhook'),
]