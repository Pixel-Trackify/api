from django.contrib import admin
from django.urls import path, include
from views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path('api/', include('authentication.urls')),
    path('auth/', include('allauth.urls')),
    path('api/', include('plans.urls')),
    path('api/', include('tutorials.urls')),
    path('api/', include('campaigns.urls')),
    path('api/', include('integrations.urls')),
    path('api/', include('payments.urls')),
    path('', index, name='index'),

]
