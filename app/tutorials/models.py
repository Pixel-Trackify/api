from django.db import models
import requests
import uuid


class Tutorial(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(max_length=200)
    thumbnail_url = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tutorials'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para buscar e salvar a URL da miniatura
        automaticamente se ela não estiver definida.
        """
        if not self.thumbnail_url:
            self.thumbnail_url = self.get_thumbnail_url()
        super().save(*args, **kwargs)

    def get_thumbnail_url(self):
        """
        Faz uma requisição à API de oEmbed do YouTube para obter os dados do vídeo,
        incluindo a URL da miniatura.
        """
        oembed_url = f"https://www.youtube.com/oembed?url={self.youtube_url}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            data = response.json()
            return data.get('thumbnail_url')
        return ''
