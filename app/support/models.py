import uuid
from django.db import models
from django.contrib.auth import get_user_model

# Obtém o modelo de usuário configurado no projeto
User = get_user_model()


class Support(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="supports"
    )
    admin_read = models.BooleanField(default=False)
    user_read = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)
    total_replies = models.IntegerField(default=0)
    title = models.CharField(max_length=255)
    description = models.TextField()
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'support'


class SupportReply(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    support = models.ForeignKey(
        Support, on_delete=models.CASCADE, related_name="replies"
    )  # Relaciona a resposta ao suporte correspondente
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Relaciona a resposta ao usuário que a criou
    role = models.CharField(
        max_length=20, choices=(("user", "User"), ("is_superuser", "Admin"))
    )  # Identifica se a resposta foi feita por um usuário ou admin
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reply to {self.support.title}"

    class Meta:
        db_table = 'support_replies'


class SupportReplyAttachment(models.Model):
    id = models.AutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    support = models.ForeignKey(
        Support, on_delete=models.CASCADE, null=True, blank=True, related_name="attachments"
    )  # Relaciona o anexo ao suporte
    support_reply = models.ForeignKey(
        SupportReply, on_delete=models.CASCADE, null=True, blank=True, related_name="attachments"
    )  # Relaciona o anexo à resposta
    file = models.URLField(max_length=500, null=True,
                           blank=True)  # URL do arquivo anexado
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de atualização

    def __str__(self):
        return f"Attachment for {self.support or self.support_reply}"

    class Meta:
        db_table = 'support_replies_attachment'  # Nome da tabela no banco de dados
