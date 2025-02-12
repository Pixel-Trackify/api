from django.contrib import admin
from django.urls import path, include




urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('authentication.urls')),
    path('auth/', include('allauth.urls')),
    path('api/', include('plans.urls')),
   
]
