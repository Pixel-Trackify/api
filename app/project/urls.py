from django.contrib import admin
from django.urls import path, include
from views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('authentication.urls')),
    path('auth/', include('allauth.urls')),
    path('', include('plans.urls')),
    path('', include('tutorials.urls')),
    path('', include('campaigns.urls')),
    path('', include('integrations.urls')),
    path('', include('payments.urls')),
    path('', index, name='index'),

]
