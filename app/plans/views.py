from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import generics, filters
from rest_framework import status
from .models import Plan
from .serializers import PlanSerializer
from .schema import plan_viewset_schema, multiple_delete_schema

from .permissions import IsAdminUserOrReadOnly


@plan_viewset_schema
class PlanViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de Planos (GET público, modificações restritas a admins)"""
    queryset = Plan.objects.all().prefetch_related('features')
    serializer_class = PlanSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [filters.OrderingFilter,
                       filters.SearchFilter]
    ordering_fields = ['created_at', 'price']
    ordering = ['-created_at']
    search_fields = ['name']
    lookup_field = 'uid'
    http_method_names = ['get', 'post', 'put', 'delete']

    @multiple_delete_schema
    @action(detail=False, methods=['post'], url_path='multiple-delete')
    def multiple_delete(self, request, *args, **kwargs):
        """
        Permite que administradores excluam múltiplos planos de uma vez.
        - Recebe uma lista de UIDs no corpo da requisição.
        """
        uids = request.data.get('uids', [])
        if not isinstance(uids, list) or not uids:
            return Response(
                {"error": "Nenhum UUID fornecido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        deleted_count, _ = Plan.objects.filter(uid__in=uids).delete()
        return Response(
            {"detail": f"planos foram excluídos com sucesso."},
            status=status.HTTP_200_OK
        )


