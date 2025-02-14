from django.db import models


class Tutorial(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    youtube_url = models.URLField(max_length=200)
    thumbnail_url = models.URLField(max_length=200, blank=True)

    def __str__(self):
        return self.title
