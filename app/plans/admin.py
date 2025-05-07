from django.contrib import admin
from .models import Plan, PlanFeature


class PlanFeatureInline(admin.TabularInline):
    """Permite adicionar características diretamente na página do Plano no Admin"""
    model = PlanFeature
    extra = 1  # Número de campos extras para adição rápida


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    """Configuração do Admin para Planos"""
    list_display = ('name', 'price', 'duration',
                    'is_current')  # Colunas na lista
    inlines = [PlanFeatureInline]  # Integra características
