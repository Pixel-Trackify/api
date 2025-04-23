from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminUserOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from .models import Goal
from .serializers import GoalSerializer
from drf_spectacular.utils import extend_schema
from .schemas import (delete_goal_schema, delete_multiple_goals_schema, list_goals_schema,
                      create_goal_schema,
                      retrieve_goal_schema,
                      update_goal_schema,)


class GoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar metas.
    """
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    lookup_field = 'uid'
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['prize', 'created_at']
    search_fields = ['prize', 'description']

    def get_queryset(self):
        user = self.request.user

        # Usuários autenticados podem acessar todas as metas
        if user.is_authenticated:
            queryset = self.queryset

            # Se for administrador, permite filtros e ordenação
            if user.is_superuser:
                prize = self.request.query_params.get('prize', None)
                description = self.request.query_params.get(
                    'description', None)

                if prize:
                    queryset = queryset.filter(prize__icontains=prize)
                if description:
                    queryset = queryset.filter(
                        description__icontains=description)

            return queryset

        # Usuários não autenticados não têm acesso
        return self.queryset.none()

    @extend_schema(**list_goals_schema)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**create_goal_schema)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(**retrieve_goal_schema)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(**update_goal_schema)
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(**update_goal_schema)
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(**delete_goal_schema)
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Meta excluída com sucesso."},
            status=status.HTTP_200_OK
        )

    def perform_destroy(self, instance):

        if not self.request.user.is_superuser:
            raise PermissionDenied(
                "Você não tem permissão para deletar esta meta.")
        instance.delete()

    @extend_schema(**delete_multiple_goals_schema)
    @action(detail=False, methods=['post'], url_path='delete-multiple')
    def delete_multiple(self, request):

        uids = request.data.get('uids', None)
        if not uids:
            return Response(
                {"error": "Nenhum UUID fornecido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Busca as metas correspondentes
        instances = self.get_queryset().filter(uid__in=uids)
        not_found_uids = set(
            uids) - set(instances.values_list('uid', flat=True))

        # Usa uma transação para garantir consistência
        with transaction.atomic():
            deleted_count = instances.delete()[0]

        # Retorna uma resposta detalhada
        return Response(
            {
                "message": f"{deleted_count} meta(s) excluída(s) com sucesso.",
                # Lista de UUIDs não encontrados
                "not_found": list(not_found_uids)
            },
            status=status.HTTP_200_OK
        )
