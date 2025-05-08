from django.urls import path
from .views import PaymentView, PaymentStatusView, PaymentWebhookView

urlpatterns = [
    path('payments/', PaymentView.as_view(),
         name='payments'),
    path('payments/<uuid:uid>/', PaymentStatusView.as_view(), name='payment-status'),
    path('webhook/zeroone/',
         PaymentWebhookView.as_view(), name='payment-webhook'),

]
