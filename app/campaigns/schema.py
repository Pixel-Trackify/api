from drf_spectacular.utils import extend_schema, extend_schema_view
from .serializers import CampaignSerializer, CampaignViewSerializer

schemas = {
    'campaign_view_set': extend_schema_view(
        list=extend_schema(
            description="Retorna as campanhas do usuário autenticado.",
            responses={200: CampaignSerializer(many=True)}
        ),
        create=extend_schema(
            description="Cria uma nova campanha vinculada ao usuário autenticado.",
            request=CampaignSerializer,
            responses={201: CampaignSerializer}
        ),
        retrieve=extend_schema(
            description="Retorna os detalhes de uma campanha específica do usuário autenticado.",
            responses={200: CampaignSerializer}
        ),
        update=extend_schema(
            description="Atualiza uma campanha se o usuário autenticado for o proprietário.",
            request=CampaignSerializer,
            responses={200: CampaignSerializer}
        ),
        partial_update=extend_schema(
            description="Atualiza parcialmente uma campanha se o usuário autenticado for o proprietário.",
            request=CampaignSerializer,
            responses={200: CampaignSerializer}
        ),
        destroy=extend_schema(
            description="Deleta uma campanha se o usuário autenticado for o proprietário.",
            responses={204: None}
        )
    ),
    'kwai_webhook_view': extend_schema_view(
        get=extend_schema(
            description="Atualiza a campanha com base na ação recebida (view ou click).",
            responses={200: CampaignViewSerializer}
        )
    )
}