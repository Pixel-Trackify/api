from rest_framework import serializers
from .models import Plan, PlanFeature, UserSubscription

class PlanFeatureSerializer(serializers.ModelSerializer):
    """Serializa as características dos planos (relacionamento 1:N)"""
    class Meta:
        model = PlanFeature
        fields = ('text',)  # Apenas o texto da característica

class PlanSerializer(serializers.ModelSerializer):
    """Serializador principal para Planos (inclui características)"""
    features = PlanFeatureSerializer(
        many=True,
        read_only=True,  # Não permite escrita direta (gerenciado via admin)
        source='features.all'  # Busca todas as características relacionadas
    )

    class Meta:
        model = Plan
        fields = (
            'id', 'uid', 'name', 'price', 'duration',
            'duration_value', 'is_current', 'description', 'features'
        )  # Campos expostos na API

class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializador para assinaturas de usuários"""
    class Meta:
        model = UserSubscription
        fields = ('id', 'plan', 'start_date', 'end_date', 'is_active')
        read_only_fields = ('user', 'start_date', 'is_active')  # Campos automáticos

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuário não autenticado.")

        user = request.user
        if UserSubscription.objects.filter(user=user, is_active=True).exists():
            raise serializers.ValidationError("Você já tem uma assinatura ativa.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        plan = validated_data.get('plan')

        # Cria a assinatura do usuário
        subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            end_date=validated_data.get('end_date')
        )

        return subscription