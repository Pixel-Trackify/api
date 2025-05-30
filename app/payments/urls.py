from django.urls import path
from . import views

urlpatterns = [
    path('payments/', views.PaymentCreateView.as_view(),
         name='payments'),
    path('payments/change/<uuid:uid>/', views.PaymentChangePlanView.as_view(),
         name='payment-change-plan'),
    path('subscription/', views.SubscriptionInfoView.as_view(),
         name='subscription-info'),
    path('payments/<uuid:uid>/status/',
         views.PaymentStatusView.as_view(), name='payment-status'),
    path('webhook/zeroone/',
         views.PaymentWebhookView.as_view(), name='payment-webhook'),

]
