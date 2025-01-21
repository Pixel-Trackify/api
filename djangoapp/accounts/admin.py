from django.contrib import admin
from accounts.models import Accounts
# Register your models here.

@admin.register(Accounts)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'cpf')