from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IntegrationViewSet, IntegrationDetailView, AvailableGatewaysView

router = DefaultRouter()
router.register(r'integrations-user', IntegrationViewSet,
                basename='integration')

urlpatterns = [
    path('', include(router.urls)),
    path('integration/<uuid:uid>/', IntegrationDetailView.as_view(),
         name='integration-detail'),
    path('integrations/gateways/', AvailableGatewaysView.as_view(),
         name='available-gateways'),

]
