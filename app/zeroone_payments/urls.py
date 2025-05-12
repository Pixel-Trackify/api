from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentCreateView.as_view(),
         name='payments'),
    path('payments/change/<uuid:uid>/', views.PaymentChangePlanView.as_view(),
         name='payment-change-plan'),
    path('payments/<uuid:uid>/status/',
         views.PaymentStatusView.as_view(), name='payment-status'),
    path('webhook/zeroone/',
         views.PaymentWebhookView.as_view(), name='payment-webhook'),

]
