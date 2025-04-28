from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUserOrReadOnly(BasePermission):
    """
    Permite acesso de leitura para todos, mas apenas administradores podem criar, atualizar ou deletar.
    """

    def has_permission(self, request, view):
        # Permite métodos seguros (GET, HEAD, OPTIONS) para todos
        if request.method in SAFE_METHODS:
            return True

        # Permite métodos de escrita apenas para administradores
        return request.user and request.user.is_superuser
