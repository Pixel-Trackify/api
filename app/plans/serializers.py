from rest_framework import serializers
from .models import Plan, PlanFeature, UserSubscription


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ['text', 'active']


class PlanSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, write_only=True)
    # Campo para exibir as features na resposta
    features_response = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        fields = [
            'uid', 'name', 'price', 'duration', 'duration_value',
            'is_current', 'description', 'created_at', 'features', 'features_response'
        ]  # Incluímos 'features_response' aqui
        read_only_fields = ['uid', 'created_at']

    def get_features_response(self, instance):
        """Inclui as features na resposta"""
        return [
            {"text": feature.text, "active": feature.active}
            for feature in instance.features.all()
        ]

    def validate(self, data):
        """Valida os dados do plano"""
        price = data.get('price')
        if price is not None and price <= 0:
            raise serializers.ValidationError(
                {"price": "O preço deve ser maior que 0."})
        return data

    def create(self, validated_data):
        features_data = validated_data.pop('features', [])
        plan = Plan.objects.create(**validated_data)
        for feature_data in features_data:
            PlanFeature.objects.create(plan=plan, **feature_data)
        return plan

    def update(self, instance, validated_data):
        """Atualiza o plano e suas features"""
        features_data = validated_data.pop('features', [])

        # Atualiza os campos do plano
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Atualiza as features
        instance.features.all().delete()
        for feature_data in features_data:
            PlanFeature.objects.create(plan=instance, **feature_data)

        return instance


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializador para assinaturas de usuários"""
    class Meta:
        model = UserSubscription
        fields = ('id', 'plan', 'start_date', 'end_date', 'is_active')
        read_only_fields = ('user', 'start_date',
                            'is_active')  # Campos automáticos

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuário não autenticado.")

        user = request.user
        if UserSubscription.objects.filter(user=user, is_active=True).exists():
            raise serializers.ValidationError(
                "Você já tem uma assinatura ativa.")
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


# swagger

class PlanCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(
        max_length=500)
    price = serializers.FloatField()
    duration = serializers.CharField(max_length=50)
    duration_value = serializers.IntegerField()
    features = serializers.ListField(
        child=PlanFeatureSerializer(),

    )


class PlanUpdateSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, write_only=True)

    class Meta:
        model = Plan
        fields = ['name', 'description', 'price',
                  'duration', 'duration_value', 'features']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser maior que 0.")
        return value


class MultipleDeleteSerializer(serializers.Serializer):
    uids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Lista de UIDs dos planos a serem excluídos.",

    )
