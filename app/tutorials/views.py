from rest_framework import generics, permissions
from .models import Tutorial
from .serializers import TutorialSerializer

# Permissão personalizada para permitir apenas administradores para métodos não seguros
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Permite métodos seguros para qualquer usuário
        if request.method in permissions.SAFE_METHODS:
            return True
        # Permite métodos não seguros apenas para administradores
        return request.user and request.user.is_superuser

# View para listar tutoriais (qualquer usuário pode visualizar)
class TutorialListView(generics.ListAPIView):
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# View para criar tutoriais (apenas administradores podem criar)
class TutorialCreateView(generics.CreateAPIView):
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [permissions.IsAdminUser]

# View para recuperar, atualizar e deletar tutoriais (apenas administradores podem editar e deletar)
class TutorialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tutorial.objects.all()
    serializer_class = TutorialSerializer
    permission_classes = [IsAdminOrReadOnly]