from rest_framework import generics, permissions
from .models import Tutorial
from .serializers import TutorialSerializer


# View para listar e criar tutoriais
class TutorialListCreateView(generics.ListCreateAPIView):
    queryset = Tutorial.objects.all()  
    serializer_class = TutorialSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Permissões padrão: autenticado ou somente leitura

    def get_permissions(self):
        # Se o método for seguro (GET, HEAD ou OPTIONS), qualquer usuário autenticado pode acessar
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        # Para métodos não seguros (POST, PUT, DELETE), apenas administradores podem acessar
        return [permissions.IsAdminUser()]

# View para recuperar, atualizar e deletar tutoriais


class TutorialRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tutorial.objects.all()  
    serializer_class = TutorialSerializer  
    # Permissões padrão: autenticado ou somente leitura
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # Se o método for seguro (GET, HEAD ou OPTIONS), qualquer usuário autenticado pode acessar
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        # Para métodos não seguros (POST, PUT, DELETE), apenas administradores podem acessar
        return [permissions.IsAdminUser()]
