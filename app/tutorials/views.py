from rest_framework import generics, permissions, filters
from .models import Tutorial
from .serializers import TutorialSerializer
from .schemas import tutorial_create_schema, tutorial_list_schema, tutorial_detail_schema


# Permissão personalizada para permitir apenas administradores para métodos não seguros
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


@tutorial_create_schema
class TutorialCreateView(generics.CreateAPIView):
    """
    View para criar novos tutoriais.
    """
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAdminUser]


@tutorial_list_schema
class TutorialListView(generics.ListAPIView):
    """
    View para listar tutoriais com paginação, ordenação e busca.
    """
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'title', 'description']
    ordering = ['id']
    search_fields = ['id', 'title', 'description']

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get(
            'ordering', 'id')  # Campo de ordenação
        order = self.request.query_params.get(
            'order', 'asc')  # Direção da ordenação

        # Valida o campo de ordenação
        if ordering not in self.ordering_fields:
            ordering = 'id'

        # Aplica a direção da ordenação
        if order == 'desc':
            ordering = f'-{ordering}'

        return queryset.order_by(ordering)


@tutorial_detail_schema
class TutorialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    View para recuperar, atualizar e deletar tutoriais.
    """
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'uid'
