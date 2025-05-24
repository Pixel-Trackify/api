from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register('admin-dashboard', views.AdminDashboardViewSet,
                basename='admin-dashboard')

urlpatterns = [
    path('configuration/', views.ConfigurationView.as_view(), name='configuration'),
    path('captcha/', views.CaptchaView.as_view(), name='captcha'),
    path('subscription-report/',
         views.AdminSubscriptionReportView.as_view()),
]


urlpatterns += router.urls
