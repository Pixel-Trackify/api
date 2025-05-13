from django.contrib import admin
from django.urls import path, include
from views import index
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('authentication.urls')),
    path('', include('plans.urls')),
    path('', include('tutorials.urls')),
    path('', include('campaigns.urls')),
    path('', include('integrations.urls')),
    path('', include('support.urls')),
    path('', include('goals.urls')),
    path('', include('kwai.urls')),
    path('', include('custom_admin.urls')),
    path('', include('payments.urls')),

    path('api/schema/', SpectacularAPIView.as_view(),
         name='schema'),  # URL para gerar o esquema OpenAPI
    # URLs para visualizações da documentação
    path('api/docs/swagger/',
         SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/',
         SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]
