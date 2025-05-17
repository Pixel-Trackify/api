from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample, OpenApiTypes
from .serializers import CampaignSerializer, CampaignViewSerializer, PaginationMetadataSerializer


schemas = {
    'campaign_view_set': extend_schema_view(
        list=extend_schema(
            summary="Listar campanhas com suporte a paginação, ordenação e busca.",
            description="Endpoint para listar as campanhas do usuário autenticado com suporte a paginação, ordenação e busca.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="page",
                    description="Número da página para paginação.",
                    required=False,
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                ),
                OpenApiParameter(
                    name="page_size",
                    description="Número de itens por página.",
                    required=False,
                    type=OpenApiTypes.INT,
                    location=OpenApiParameter.QUERY,
                ),
                OpenApiParameter(
                    name="ordering",
                    description=(
                        "Campo para ordenação. Use os campos disponíveis: `id`, `title`, `created_at`. "
                        "Exemplo: `?ordering=title` para ordenar por título."
                    ),
                    required=False,
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                ),
                OpenApiParameter(
                    name="search",
                    description=(
                        "Palavra-chave para busca nos campos definidos: `id`, `title`, `description`, `created_at`. "
                        "Exemplo: `?search=Campanha` para buscar campanhas relacionadas a 'Campanha'."
                    ),
                    required=False,
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                ),
                OpenApiParameter(
                    name="search",
                    description="Busca campanhas pelo título ou data de criação. Aceita apenas caracteres alfanuméricos e alguns caracteres especiais.",
                    required=False,
                    type=OpenApiTypes.STR,
                ),
                OpenApiParameter(
                    name="start",
                    description="Data inicial no formato YYYY-MM-DD. Filtra campanhas criadas a partir desta data.",
                    required=False,
                    type=OpenApiTypes.DATE,
                ),
                OpenApiParameter(
                    name="end",
                    description="Data final no formato YYYY-MM-DD. Filtra campanhas criadas até esta data.",
                    required=False,
                    type=OpenApiTypes.DATE,
                ),
            ],
            responses={
                200: {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "example": 3},
                        "next": {"type": "string", "example": "http://localhost:8000/campaigns/?page=2"},
                        "previous": {"type": "string", "example": None},
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "uid": {"type": "string", "example": "7201a40f-c432-42f7-b875-0d77077990ab"},
                                    "title": {"type": "string", "example": "Campanha ZeroOne"},
                                    "description": {"type": "string", "example": "Descrição da campanha"},
                                    "CPM": {"type": "number", "example": 12.0},
                                    "created_at": {"type": "string", "example": "2025-03-31T10:00:00Z"},
                                },
                            },
                        },
                    },
                },
                404: {
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "example": "Nenhuma campanha encontrada com os critérios de busca."},
                    },
                },
            },
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição com Ordenação",
                    value={
                        "url": "http://localhost:8000/campaigns/?ordering=title"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Requisição com Paginação",
                    value={
                        "url": "http://localhost:8000/campaigns/?page=2&page_size=1"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Requisição com Busca",
                    value={
                        "url": "http://localhost:8000/campaigns/?search=Campanha"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Ordenação)",
                    value={
                        "count": 3,
                        "next": 'null',
                        "previous": 'null',
                        "results": [
                            {
                                "uid": "e0522530-bf1f-4df0-9a1a-8a3ca25e4cf1",
                                "title": "Campanha 2",
                                "description": "Descrição da campanha 2",
                                "CPM": 15.0,
                                "created_at": "2025-03-30T10:00:00Z"
                            },
                            {
                                "uid": "7201a40f-c432-42f7-b875-0d77077990ab",
                                "title": "Campanha ZeroOne",
                                "description": "Descrição da campanha",
                                "CPM": 12.0,
                                "created_at": "2025-03-31T10:00:00Z"
                            }
                        ]
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Paginação)",
                    value={
                        "count": 3,
                        "next": "http://localhost:8000/campaigns/?page=3&page_size=1",
                        "previous": "http://localhost:8000/campaigns/?page=1&page_size=1",
                        "results": [
                            {
                                "uid": "e0522530-bf1f-4df0-9a1a-8a3ca25e4cf1",
                                "title": "Campanha 2",
                                "description": "Descrição da campanha 2",
                                "CPM": 15.0,
                                "created_at": "2025-03-30T10:00:00Z"
                            }
                        ]
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Busca)",
                    value={
                        "count": 2,
                        "next": 'null',
                        "previous": 'null',
                        "results": [
                            {
                                "uid": "7201a40f-c432-42f7-b875-0d77077990ab",
                                "title": "Campanha ZeroOne",
                                "description": "Descrição da campanha",
                                "CPM": 12.0,
                                "created_at": "2025-03-31T10:00:00Z"
                            },
                            {
                                "uid": "e0522530-bf1f-4df0-9a1a-8a3ca25e4cf1",
                                "title": "Campanha 2",
                                "description": "Descrição da campanha 2",
                                "CPM": 15.0,
                                "created_at": "2025-03-30T10:00:00Z"
                            }
                        ]
                    },
                    response_only=True,
                ),
            ],
        ),
        create=extend_schema(
            summary="Criar uma nova campanha",
            description=(
                "Endpoint para criar uma nova campanha vinculada ao usuário autenticado. "
                "Não é permitido usar gateways que já estão em uso por outras campanhas."
            ),
            tags=["Campanhas"],
            request=CampaignSerializer,
            responses={
                201: CampaignSerializer,
                400: {
                    "type": "object",
                    "properties": {
                        "integrations": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "example": "O gateway 'ZeroOne' já está em uso."
                            }
                        }
                    },
                    "example": {
                        "integrations": [
                            "O gateway 'ZeroOne' já está em uso."
                        ]
                    }
                }
            },
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "title": "Campanha ZeroOne",
                        "description": "Descrição da nova campanha",
                        "CPM": 12,
                        "integrations": ["846ec04e-2d7b-4343-83f8-dd36776401eb"]
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Sucesso)",
                    value={
                        "id": 9,
                        "uid": "57c111f3-02b9-4006-b95c-68b1d1b04351",
                        "integrations": [
                            "846ec04e-2d7b-4343-83f8-dd36776401eb"
                        ],
                        "user": "6f4191cb-0943-4854-a307-cda83b99126e",
                        "source": "Kwai",
                        "title": "Cursinho",
                        "CPM": "3.70",
                        "total_approved": 0,
                        "total_pending": 0,
                        "amount_approved": "0.00",
                        "amount_pending": "0.00",
                        "total_abandoned": 0,
                        "amount_abandoned": "0.00",
                        "total_canceled": 0,
                        "amount_canceled": "0.00",
                        "total_refunded": 0,
                        "amount_refunded": "0.00",
                        "total_rejected": 0,
                        "amount_rejected": "0.00",
                        "total_chargeback": 0,
                        "amount_chargeback": "0.00",
                        "total_ads": "0.00620000",
                        "profit": "0",
                        "ROI": "0",
                        "total_views": 0,
                        "total_clicks": 0,
                        "created_at": "2025-03-26T16:52:09.109455-03:00",
                        "updated_at": "2025-03-26T16:52:09.132047-03:00",

                        "stats": {
                                "pix": 0,
                                "credit_card": 0,
                                "credit_debit": 0,
                                "boleto": 0
                        },
                        "overviews": [],
                        "view_webhook_url": "http://localhost/webhook/kwai/1759be9f-f0f3-40ae-ad24-0e01c3b86e7f/?action=view",
                        "click_webhook_url": "http://localhost/webhook/kwai/1759be9f-f0f3-40ae-ad24-0e01c3b86e7f/?action=click",

                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Erro - Gateway em Uso)",
                    value={
                        "integrations": [
                            "O gateway 'ZeroOne' já está em uso."
                        ]
                    },
                    response_only=True,
                )
            ],
        ),

        retrieve=extend_schema(
            summary="Recuperar uma campanha",
            description="Endpoint para recuperar os detalhes de uma campanha específica usando o UUID como identificador.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser recuperada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Resposta",
                    value=[
                        {
                            "id": 9,
                            "uid": "57c111f3-02b9-4006-b95c-68b1d1b04351",
                            "integrations": [
                                "846ec04e-2d7b-4343-83f8-dd36776401eb"
                            ],
                            "user": "6f4191cb-0943-4854-a307-cda83b99126e",
                            "source": "Kwai",
                            "title": "Cursinho",
                            "CPM": "3.70",
                            "total_approved": 0,
                            "total_pending": 0,
                            "amount_approved": "0.00",
                            "amount_pending": "0.00",
                            "total_abandoned": 0,
                            "amount_abandoned": "0.00",
                            "total_canceled": 0,
                            "amount_canceled": "0.00",
                            "total_refunded": 0,
                            "amount_refunded": "0.00",
                            "total_rejected": 0,
                            "amount_rejected": "0.00",
                            "total_chargeback": 0,
                            "amount_chargeback": "0.00",
                            "total_ads": "0.000000",
                            "profit": "0",
                            "ROI": "0",
                            "total_views": 0,
                            "total_clicks": 0,
                            "created_at": "2025-03-26T16:52:09.109455-03:00",
                            "updated_at": "2025-03-26T16:52:09.132047-03:00",
                            "stats": {
                                "pix": 0,
                                "credit_card": 0,
                                "credit_debit": 0,
                                "boleto": 0
                            },
                            "overviews": [
                                {
                                    "type": "EXPENSE",
                                    "value": 0.000,
                                    "date": "2025-04-02"
                                },
                                {
                                    "type": "REVENUE",
                                    "value": 000.0,
                                    "date": "2025-04-02"
                                },
                            ]
                        }


                    ],
                    response_only=True,
                )
            ],
        ),
        update=extend_schema(
            summary="Atualizar uma campanha",
            description="Endpoint para atualizar completamente os detalhes de uma campanha específica.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser atualizada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            request=CampaignSerializer,
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "title": "Campanha Atualizada",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 15,
                        "source": "Kwai"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha Atualizada",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 15,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),
        partial_update=extend_schema(
            summary="Atualizar parcialmente uma campanha",
            description="Endpoint para atualizar parcialmente os detalhes de uma campanha específica.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser atualizada parcialmente.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            request=CampaignSerializer,
            responses={200: CampaignSerializer},
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição",
                    value={
                        "CPM": 20
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta",
                    value={
                        "uid": "123e4567-e89b-12d3-a456-426614174000",
                        "title": "Campanha ZeroOne",
                        "integrations": ["90490bae-7ebe-4f44-9ebf-ce81ee03e60f"],
                        "CPM": 20,
                        "source": "Kwai",
                        "created_at": "2025-03-20T12:00:00Z"
                    },
                    response_only=True,
                )
            ],
        ),

        destroy=extend_schema(
            summary="Deletar uma campanha",
            description="Endpoint para deletar uma campanha específica usando o UUID como identificador.",
            tags=["Campanhas"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UUID da campanha a ser deletada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH,
                )
            ],
            responses={204: None},
        )
    ),
    'kwai_webhook_view': extend_schema_view(
        get=extend_schema(
            summary="Atualizar campanha via webhook Kwai",
            description="Atualiza a campanha com base na ação recebida (view ou click).",
            tags=["Webhooks"],
            parameters=[
                OpenApiParameter(
                    name="uid",
                    description="UID da campanha a ser atualizada.",
                    required=True,
                    type=OpenApiTypes.UUID,
                    location=OpenApiParameter.PATH
                ),
                OpenApiParameter(
                    name="action",
                    description="Ação realizada (view ou click).",
                    required=False,
                    type=OpenApiTypes.STR,
                    location=OpenApiParameter.QUERY,
                    enum=["view", "click"]
                )
            ],
            responses={
                200: OpenApiTypes.OBJECT,

            },
            examples=[
                OpenApiExample(
                    "Exemplo de Requisição (View)",
                    value={
                        "url": "http://localhost:80/webhook/kwai/3b0a3cdd-b9d2-4e2a-8c32-352a65870e8a?action=view"
                    },
                    request_only=True,
                ),

                OpenApiExample(
                    "Exemplo de Requisição (Click)",
                    value={
                        "url": "http://localhost:80/webhook/kwai/3b0a3cdd-b9d2-4e2a-8c32-352a65870e8a?action=click"
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Sucesso)",
                    value={
                        "status": "success",
                        "message": "Campaign updated successfully."
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Erro de Validação - 400)",
                    value={
                        "error": "O parâmetro 'action' é obrigatório e deve ser 'view' ou 'click'."
                    },
                    response_only=True,
                ),
                OpenApiExample(
                    "Exemplo de Resposta (Campanha Não Encontrada - 404)",
                    value={
                        "detail": "Not found."
                    },
                    response_only=True,
                )
            ]
        )
    )
}
