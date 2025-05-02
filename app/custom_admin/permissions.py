from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Permite acesso apenas para usuários com is_superuser=True.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
