from rest_framework import serializers
from django.db.models import Q
from .models import Goal
from .utils import upload_to_s3


class GoalSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Goal
        fields = ['uid', 'prize', 'image',
                  'min', 'max', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validações gerais para o modelo Goal.
        """
        min_value = data.get('min', 0)
        max_value = data.get('max', 0)

        if min_value < 0 or max_value <= 0:
            raise serializers.ValidationError(
                "Os valores 'min' e 'max' devem ser maiores que 0.")

        if max_value < min_value:
            raise serializers.ValidationError(
                "O valor 'max' não pode ser menor que o valor 'min'.")

        # Validação: range de valores já cadastrado
        instance = self.instance
        query = Q(min__lte=min_value, max__gte=min_value) | Q(
            min__lte=max_value, max__gte=max_value)
        if instance:
            # Exclui o registro atual da validação
            query &= ~Q(uid=instance.uid)
        if Goal.objects.filter(query).exists():
            raise serializers.ValidationError(
                "O intervalo de valores já foi cadastrado.")

        return data

    def validate_image(self, image):
        """
        Validação para o campo de imagem.
        """
        if image and not image.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise serializers.ValidationError(
                "A imagem deve estar no formato PNG, JPG ou JPEG.")
        return image

    def create(self, validated_data):
        """
        Sobrescreve o método create para fazer o upload da imagem ao S3.
        """
        image = validated_data.pop('image', None)
        user = self.context['request'].user
        if image:
            validated_data['image'] = upload_to_s3(
                image, user)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Sobrescreve o método update para fazer o upload da imagem ao S3.
        """
        image = validated_data.pop('image', None)
        user = self.context['request'].user
        if image:
            validated_data['image'] = upload_to_s3(
                image, user)
        return super().update(instance, validated_data)
