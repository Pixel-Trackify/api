import django_filters
from .models import Plan


class PlanFilter(django_filters.FilterSet):
    """Filtros personalizados para Planos (ex: /plans/?price__lte=500)"""
    price__lte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',  # Preço menor ou igual (<=)
        help_text="Filtrar por preço máximo"
    )
    price__gte = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',  # Preço maior ou igual (>=)
        help_text="Filtrar por preço mínimo"
    )

    class Meta:
        model = Plan
        fields = ['duration', 'is_current']  # Filtros diretos por campos
