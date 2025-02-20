from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("uid", "name", "email", "cpf", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("email", "cpf", "name")
    ordering = ("uid",)
    # Campos que não podem ser editados
    readonly_fields = ("date_joined", "locked_until", "login_attempts")
    fieldsets = (
        ("Informações Pessoais", {"fields": ("name", "email", "cpf")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Controle de Acesso", {
         "fields": ("password", "login_attempts", "locked_until")}),
        ("Datas", {"fields": ("date_joined",)}),
    )

    # Removendo a opção de adicionar usuário pelo Django Admin
    
    
    def has_add_permission(self, request):
        return False




