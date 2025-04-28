from rest_framework.permissions import BasePermission


class IsAdminUserForList(BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores
    possam listar todos os usuários.
    """

    def has_permission(self, request, view):
        # Verifica se a ação é 'list' e se o usuário é administrador
        if view.action == 'list':
            return request.user and request.user.is_superuser

        # Para outras ações, permite o acesso
        return True