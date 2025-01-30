from django_filters import rest_framework as filters
from .models import Usuario


class UsuarioFilter(filters.FilterSet):
    min_id = filters.NumberFilter(field_name="id", lookup_expr="gte")
    max_id = filters.NumberFilter(field_name="id", lookup_expr="lte")
    created_after = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Usuario
        fields = ['name', 'email', 'min_id', 'max_id',
                  'created_after', 'created_before']
