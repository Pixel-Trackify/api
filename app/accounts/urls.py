from django.urls import path
from . import views


urlpatterns = [
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/register-accounts/', views.RegisterView.as_view(),
         name='account-create-list'),
    path('auth/users/', views.GetUsersView.as_view(), name='user-list'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),
    path('auth/change-password/',
         views.ChangePasswordView.as_view(), name='change_password'),
    path('auth/update-plan/', views.UpdateUserPlanView.as_view(), name='update-plan'),
    path('auth/subscription-history/', views.UserSubscriptionHistoryView.as_view(), name='subscription-history'),
    path('auth/my-plan/', views.UserPlanView.as_view(), name='my-plan'),
    path('auth/accounts/<uuid:uuid>',views.AccountRetrieveUpdateDestroyView.as_view(), name='account-detail-view'),
    path('auth/filter-users/', views.FilterUsersView.as_view(), name='filter-users'),

]
