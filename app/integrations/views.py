from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Integration
from .serializers import IntegrationSerializer


class IntegrationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar integrações.
    """
    queryset = Integration.objects.all()
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna as integrações do usuário autenticado.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Salva a nova integração com o usuário autenticado.
        """
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """
        Atualiza a integração se o usuário autenticado  o proprietário.
        """
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        """
        Deleta a integração se o usuário autenticado for o proprietário.
        """
        if instance.user != self.request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        instance.delete()


class IntegrationDetailView(APIView):
    """
    APIView para gerenciar uma integração específica.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        """
        Retorna os detalhes de uma integração específica do usuário autenticado.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user)
        serializer = IntegrationSerializer(integration)
        return Response(serializer.data)

    def delete(self, request, uid):
        """
        Deleta uma integração específica do usuário autenticado.
        """
        integration = get_object_or_404(
            Integration, uid=uid, user=request.user)
        integration.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
