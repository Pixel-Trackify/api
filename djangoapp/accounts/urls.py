from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('accounts/', views.RegisterView.as_view(), name='account-create-list'),
    path('users/', views.GetUsersView.as_view(), name='user-list'),
    path('accounts/<int:pk>', views.AccountRetrieveUpdateDestroyView.as_view(), name='account-detail-view'),
    path('filter-users/', views.FilterUsersView.as_view(), name='filter-users'),

]
