from rest_framework.permissions import BasePermission


class IsAdminUserOrReadOnly(BasePermission):

    def has_permission(self, request, view):

        if request.method in ['GET', 'OPTIONS']:

            if view.action == 'retrieve' and not request.user.is_superuser:
                return False
            return True

        return request.user and request.user.is_superuser
