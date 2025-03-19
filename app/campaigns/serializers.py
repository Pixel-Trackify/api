from rest_framework import serializers
from .models import Campaign, CampaignView, Integration
import logging


logger = logging.getLogger(__name__)


class CampaignSerializer(serializers.ModelSerializer):
    integrations = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Integration.objects.all(),
        many=True,
        error_messages={
            'does_not_exist': "Integração não foi encontrada.",
            'invalid': "Valor inválido."
        }
    )

    class Meta:
        model = Campaign
        fields = [
            'id', 'uid', 'integrations', 'user', 'source', 'title', 'CPM',
            'total_approved', 'total_pending', 'amount_approved', 'amount_pending',
            'total_ads', 'profit', 'ROI', 'total_views', 'total_clicks',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uid', 'user', 'created_at', 'updated_at']

    def validate_CPM(self, value):
        """Valida se o CPM é maior que 0"""
        if value <= 0:
            raise serializers.ValidationError("O CPM deve ser maior que 0.")
        return value

    def validate_integrations(self, value):
        """Valida se todas as integrações pertencem ao usuário autenticado"""
        user = self.context['request'].user
        invalid_integrations = [
            integration for integration in value if integration.user != user
        ]
        if invalid_integrations:
            raise serializers.ValidationError(
                "Integrações não encontrada."
            )
        return value

    def create(self, validated_data):
        """Cria uma campanha e associa as integrações"""
        logger.debug(f"Dados validados no serializer: {validated_data}")
        integrations = validated_data.pop('integrations', [])
        try:
            campaign = Campaign.objects.create(**validated_data)
            logger.debug(f"Campanha criada no banco de dados: {campaign}")
            campaign.integrations.set(integrations)
            logger.debug(f"Integrações associadas: {integrations}")
            return campaign
        except Exception as e:
            logger.error(f"Erro ao criar a campanha: {e}")
            raise serializers.ValidationError("Erro ao salvar a campanha no banco de dados.")

    def update(self, instance, validated_data):
        """Atualiza uma campanha e associa as integrações"""
        integrations = validated_data.pop('integrations', None)
        if integrations is not None:
            instance.integrations.set(integrations)
        return super().update(instance, validated_data)


class CampaignViewSerializer(serializers.ModelSerializer):
    campaign = serializers.SlugRelatedField(
        slug_field='uid',
        queryset=Campaign.objects.all()
    )

    class Meta:
        model = CampaignView
        fields = ['id', 'campaign', 'user_agent',
                  'ip_address', 'action', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
