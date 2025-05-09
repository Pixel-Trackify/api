from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
import re
from .models import Tutorial
from .serializers import TutorialSerializer
from django.core.exceptions import PermissionDenied
from django.db import transaction


class TutorialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar tutoriais.
    """
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['title', 'description']
    ordering = ['created_at']
    search_fields = ['title', 'description', 'youtube_url']
    lookup_field = 'uid'

    def get_queryset(self):
        """
        Retorna os tutoriais disponíveis, com suporte a ordenação e busca.
        """
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', 'id')
        order = self.request.query_params.get('order', 'asc')

        # Valida o campo de ordenação
        if ordering not in self.ordering_fields:
            ordering = 'id'

        # Aplica a direção da ordenação
        if order == 'desc':
            ordering = f'-{ordering}'

        return queryset.order_by(ordering)

    def filter_queryset(self, queryset):
        """
        Sobrescreve o método filter_queryset para validar os parâmetros de busca.
        """
        queryset = super().filter_queryset(queryset)

        search_param = self.request.query_params.get('search', None)

        if search_param:

            if not re.match(r'^[a-zA-Z0-9\s\-_,\.;:()áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]+$', search_param):
                raise ValidationError(
                    {"search": "O parâmetro de busca contém caracteres inválidos."}
                )

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Sobrescreve o método list para adicionar uma mensagem de erro
        caso nenhum dado seja encontrado na busca.
        """
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(
                {"count": 0, "detail": "Nenhum tutorial encontrado com os critérios de busca.", "results": []},
                status=status.HTTP_200_OK
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Permite apenas administradores criarem tutoriais.
        """
        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Apenas administradores podem criar tutoriais.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Permite deletar um tutorial pelo `uid`.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Tutorial excluído com sucesso."},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):
        """
        Permite deletar vários tutoriais enviando os `uids` no corpo da requisição.
        """
        uids = request.data.get('uids', None)
        if not uids:
            return Response(
                {"error": "Nenhum UID fornecido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca os tutoriais correspondentes
        instances = self.get_queryset().filter(uid__in=uids)
        not_found_uids = set(
            uids) - set(instances.values_list('uid', flat=True))

        if not instances.exists():
            return Response(
                {"error": "Nenhum tutorial encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Usa uma transação para garantir consistência
        with transaction.atomic():
            deleted_count = instances.delete()[0]

        return Response(
            {
                "message": f"{deleted_count} tutorial(s) excluído(s) com sucesso.",
                "not_found": list(not_found_uids)
            },
            status=status.HTTP_200_OK
        )
