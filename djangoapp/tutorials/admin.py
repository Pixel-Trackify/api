from django.contrib import admin
from .models import Tutorial


@admin.register(Tutorial)
class TutorialAdmin(admin.ModelAdmin):
    list_display = ('title', 'youtube_url', 'thumbnail_url')
    search_fields = ('title', 'youtube_url')
