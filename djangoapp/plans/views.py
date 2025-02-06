from rest_framework import viewsets, generics, permissions
from django_filters import rest_framework as filters
from .models import Plan, UserSubscription
from .serializers import PlanSerializer, UserSubscriptionSerializer
from .filters import PlanFilter
#from .pagination import CustomPagination
from rest_framework.pagination import PageNumberPagination


class PlanViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de Planos (GET público, modificações restritas a admins)"""
    queryset = Plan.objects.all().prefetch_related('features')  # Otimiza queries
    serializer_class = PlanSerializer
    # GET sem autenticação
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]  # Habilita filtros
    filterset_class = PlanFilter  # Usa a classe de filtros personalizada
    #pagination_class = CustomPagination  # Paginação customizada

    def get_permissions(self):
        """Restringe criação/edição/exclusão a administradores"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class UserSubscriptionCreateView(generics.CreateAPIView):
    """Endpoint para criação de assinaturas (requer autenticação JWT)"""
    queryset = UserSubscription.objects.all()
    serializer_class = UserSubscriptionSerializer
    # Apenas usuários autenticados
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Vincula automaticamente o usuário logado à assinatura"""
        serializer.save(user=self.request.user)  # Usuário vem do token JWT


'''class CustomPagination(PageNumberPagination):
    """Configuração de paginação personalizada"""
    page_size = 5  # Itens por página padrão
    page_size_query_param = 'page_size'  # Parâmetro para alterar tamanho da página
    max_page_size = 100  # Limite máximo de itens por página
'''