from django.contrib import admin
from django.urls import path
from accounts.views import account_create_list_view, account_detail_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', account_create_list_view, name='account-create-list'),
    path('accounts/<int:pk>', account_detail_view, name='account-detail-view'),
   
]
