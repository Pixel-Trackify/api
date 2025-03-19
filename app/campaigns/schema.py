from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .serializers import CampaignSerializer, CampaignViewSerializer

schemas = {
    'campaign_view_set': extend_schema_view(
        list=extend_schema(
            description="Retorna todas as campanhas do usuário autenticado.",
            responses={200: CampaignSerializer(many=True)}
        ),
        retrieve=extend_schema(
            description="Retorna os detalhes de uma campanha específica do usuário autenticado.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: CampaignSerializer}
        ),
        update=extend_schema(
            description="Atualiza uma campanha se o usuário autenticado for o proprietário.",
            request=CampaignSerializer,
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={200: CampaignSerializer}
        ),
        destroy=extend_schema(
            description="Deleta uma campanha se o usuário autenticado for o proprietário.",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                )
            ],
            responses={204: None}
        )
    ),
    'kwai_webhook_view': extend_schema_view(
        get=extend_schema(
            description="Atualiza a campanha com base na ação recebida (view ou click).",
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha",
                    required=True,
                    type=str,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name="action",
                    description="Ação realizada (view ou click)",
                    required=False,
                    type=str,
                    location=OpenApiParameter.QUERY
                )
            ],
            responses={
                200: CampaignViewSerializer,
                400: OpenApiExample(
                    "Erro de validação",
                    value={"error": "Detalhes do erro"}
                )
            }
        )
    )
}
