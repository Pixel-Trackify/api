from django.urls import path
from .views import CreatePaymentView, PaymentStatusView, PaymentWebhookView, PaymentStatusCheckView, TransactionStatusView

urlpatterns = [
    path('payment/', CreatePaymentView.as_view(), name='create_payment'),
    path('payment/<uuid:uid>/', PaymentStatusView.as_view(), name='payment_status'),
    path('payment/status/<uuid:uid>/',
         PaymentStatusCheckView.as_view(), name='payment_status_check'),
    path('webhook/firebanking/', PaymentWebhookView.as_view(),
         name='payment_webhook'),
    path('transactions/<uuid:id>/', TransactionStatusView.as_view(),
         name='transaction_status'),
]
