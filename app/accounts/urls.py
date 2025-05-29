from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register-accounts/', views.RegisterView.as_view(),
         name='account-create-list'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    path('upload-avatar/', views.UploadAvatarView.as_view(), name='upload-avatar'),
    path('auth/change-password/',
         views.ChangePasswordView.as_view(), name='change_password'),
    path('password-reset/', views.PasswordResetRequestView.as_view(),
         name='password-reset-request'),
    path('password-reset/confirm/<str:recovery_code>/', views.PasswordResetConfirmView.as_view(),
         name='password-reset-confirm'),

] + router.urls
