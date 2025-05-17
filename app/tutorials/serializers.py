from rest_framework import serializers
from django.utils.html import strip_tags
from .models import Tutorial
import re
import html

class TutorialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutorial
        fields = ['uid', 'title', 'description', 'youtube_url',
                  'thumbnail_url', 'created_at', 'updated_at']

    def validate_youtube_url(self, value):
        youtube_regex = re.compile(
            r'^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$'
        )
        if not youtube_regex.match(value):
            raise serializers.ValidationError("URL do YouTube inválida.")
        return value
    
    def validate_title(self, value):
        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError("O campo só pode conter caracteres ASCII.")
        
        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError("O campo não pode conter tags HTML.")

        if len(value) < 5:
            raise serializers.ValidationError("O campo deve ter pelo menos 5 caracteres.")
        
        if len(value) > 100:
            raise serializers.ValidationError("O campo não pode exceder 100 caracteres.")
        
        return value
    

    def validate_description(self, value):
        # Campo opcional
        if not value:
            return value
       
        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError("O campo só pode conter caracteres ASCII.")
       
        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError("O campo não pode conter tags HTML.")
        
        if len(value) < 5:
            raise serializers.ValidationError("O campo deve ter pelo menos 5 caracteres.")
        
        if len(value) > 500:
            raise serializers.ValidationError("O campo não pode exceder 500 caracteres.")
        
        return value
    
    def create(self, validated_data):
        youtube_url = validated_data.get('youtube_url')
        video_id = self.extract_video_id(youtube_url)
        thumbnail_url = f'https://img.youtube.com/vi/{video_id}/hqdefault.jpg'
        validated_data['thumbnail_url'] = thumbnail_url
        return super().create(validated_data)

    def extract_video_id(self, youtube_url):
        pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(pattern, youtube_url)
        return match.group(1) if match else None
