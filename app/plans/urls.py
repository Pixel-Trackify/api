from django.urls import path, include
from rest_framework.routers import DefaultRouter
from plans.views import PlanViewSet, UserSubscriptionCreateView

# Configuração automática de rotas CRUD para Planos
router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')

urlpatterns = [
    # Rotas automáticas do ViewSet (GET /plans/, POST /plans/, etc.)
    path('', include(router.urls)),

    # Endpoint manual para criação de assinaturas
    path('subscriptions/', UserSubscriptionCreateView.as_view(),
         name='subscription-create'),

]
