import boto3
import uuid
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from datetime import datetime
from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Support, SupportReply
from .serializers import SupportSerializer, SupportReplySerializer, SupportReplyAttachment
from .schema import (
    support_list_view_schema,
    support_detail_view_schema,
    support_create_view_schema,
    support_reply_create_view_schema,
)
import logging
import re


logger = logging.getLogger('django')


@support_list_view_schema
class SupportListView(generics.ListAPIView):
    queryset = Support.objects.all()
    serializer_class = SupportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    search_fields = ['title', 'description']

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Support.objects.all()

        return Support.objects.filter(user=user)

    def filter_queryset(self, queryset):

        queryset = super().filter_queryset(queryset)

        search_param = self.request.query_params.get('search', None)

        if search_param:

            if not re.match(r'^[a-zA-Z0-9\s\-_,\.;:()áéíóúãõâêîôûçÁÉÍÓÚÃÕÂÊÎÔÛÇ]+$', search_param):
                raise ValidationError(
                    {"search": "O parâmetro de busca contém caracteres inválidos."}
                )
        return queryset


@support_detail_view_schema
class SupportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        user = request.user

        # Verifica se o ticket existe
        support = Support.objects.filter(uid=uid).first()
        if not support:
            return Response({"error": "Ticket de suporte não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        if not user.is_superuser and support.user != user:
            return Response({"error": "Você não tem permissão para acessar este ticket."}, status=status.HTTP_403_FORBIDDEN)

        if user.is_superuser:
            support.admin_read = True
        else:
            support.user_read = True
        support.save()

        support_serializer = SupportSerializer(support)

        replies = SupportReply.objects.filter(support=support)
        replies_serializer = SupportReplySerializer(replies, many=True)

        return Response({
            "message": "Detalhes do ticket recuperados com sucesso.",
            "data": {
                "ticket": support_serializer.data,
                "replies": replies_serializer.data
            }
        }, status=status.HTTP_200_OK)


@support_reply_create_view_schema
class SupportRepliesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, uid):
        user = request.user

        # Verifica se o ticket existe
        support = Support.objects.filter(uid=uid).first()
        if not support:
            return Response(
                {"count": 0, "detail": "Nenhum suporte encontrado.", "results": []},
                status=200
            )

        # Verifica permissões
        if not user.is_superuser and support.user != user:
            return Response(
                {"count": 0, "detail": "Nenhum suporte encontrado.", "results": []},
                status=200
            )

        # Obtém as respostas associadas ao suporte
        replies = SupportReply.objects.filter(support=support)

        # Serializa as respostas
        serializer = SupportReplySerializer(replies, many=True)
        return Response(
            {"total": replies.count(), "detail": "Respostas encontradas.",
             "results": serializer.data},
            status=200
        )


class FileHandler:
    @staticmethod
    def upload_to_s3(file, user, folder="support_attachments/"):
        """
        Faz o upload do arquivo para o Bucket S3 e retorna a URL pública.
        """
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_DEFAULT_REGION
        )

        if not settings.AWS_BUCKET or not settings.AWS_DEFAULT_REGION:
            raise Exception(
                "Configurações do AWS S3 estão ausentes ou inválidas.")

        current_date = datetime.now().strftime("%Y%m%d%H%M%S")
        random_filename = f"{current_date}_{uuid.uuid4().hex}{os.path.splitext(file.name)[1]}"
        file_path = f"{folder}{user.uid}/{random_filename}"

        try:
            s3.upload_fileobj(
                file,
                settings.AWS_BUCKET,
                file_path,
                ExtraArgs={'ContentType': file.content_type,
                           'ACL': 'public-read'}
            )
            file_url = f"https://{settings.AWS_BUCKET}.s3.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{file_path}"

            return file_url
        except Exception as e:
            raise Exception(f"Erro ao fazer upload do arquivo: {str(e)}")


@support_create_view_schema
class SupportCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        title = request.data.get('title')
        description = request.data.get('description')
        files = request.FILES.getlist(
            'files') or request.FILES.getlist('files[]')

        if not title or not description:
            return Response({"error": "Título e descrição são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SupportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        support = Support.objects.create(
            user=user, title=title, description=description, user_read=True
        )

        # Upload de arquivos (opcional)
        uploaded_files = []
        if files:
            try:
                for file in files:
                    file_url = FileHandler.upload_to_s3(file, user)
                    attachment = SupportReplyAttachment.objects.create(
                        support=support, file=file_url
                    )

                    # Adiciona o link à lista de arquivos retornados
                    uploaded_files.append(file_url)
            except Exception as e:

                return Response({"error": f"Erro ao fazer upload do arquivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Retorna a resposta com os links dos arquivos
        return Response({
            "message": "Ticket criado com sucesso.",
            "uid": support.uid,
            "files": uploaded_files
        }, status=status.HTTP_201_CREATED)


@support_reply_create_view_schema
class SupportReplyCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, uid):
        user = request.user

        # Verifica se o ticket existe
        support = Support.objects.filter(uid=uid).first()
        if not support:
            return Response({"error": "Ticket de suporte não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verifica permissões
        if not user.is_superuser and support.user != user:
            return Response({"error": "Você não tem permissão para responder a este ticket."}, status=status.HTTP_403_FORBIDDEN)

        # Obtém os dados da requisição
        description = request.data.get('description')
        files = request.FILES.getlist('files')

        serializer = SupportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Valida descrição
        if not description:
            return Response({"error": "Descrição é obrigatória."}, status=status.HTTP_400_BAD_REQUEST)

        # Define o papel (role) do autor da resposta
        role = "admin" if user.is_superuser else "user"

        # Atualiza os campos de leitura no ticket
        if user.is_superuser:
            support.admin_read = True
            support.user_read = False
        else:
            support.user_read = True
            support.admin_read = False
        support.save()

        # Cria a resposta
        reply = SupportReply.objects.create(
            support=support, user=user, role=role, description=description
        )

        # Upload de arquivos (opcional)
        uploaded_files = []
        if files:
            try:
                for file in files:
                    # Faz o upload do arquivo para o S3
                    file_url = FileHandler.upload_to_s3(
                        file, user, folder="support_replies_attachments/")

                    # Salva o link no banco de dados
                    attachment = SupportReplyAttachment.objects.create(
                        support_reply=reply, file=file_url
                    )

                    # Adiciona o link à lista de arquivos retornados
                    uploaded_files.append(file_url)
            except Exception as e:
                return Response({"error": f"Erro ao fazer upload do arquivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Serializar a resposta com os dados necessários
        serializer = SupportReplySerializer(reply)
        return Response({
            "message": "Resposta criada com sucesso.",
            "data": serializer.data,
            "files": uploaded_files  # Links dos arquivos enviados
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_ticket(request, uid):
    """
    Fecha um ticket de suporte.
    """
    user = request.user

    # Verifica se o ticket existe
    support = Support.objects.filter(uid=uid).first()
    if not support:
        return Response({"error": "Ticket de suporte não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    # Verifica permissões
    if not user.is_superuser and support.user != user:
        return Response({"error": "Você não tem permissão para fechar este ticket."}, status=status.HTTP_403_FORBIDDEN)

    # Marca o ticket como fechado
    support.closed = True
    support.save()

    return Response({"message": "Ticket fechado com sucesso."}, status=status.HTTP_200_OK)
