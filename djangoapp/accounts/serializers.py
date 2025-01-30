import socket
import re
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Usuario



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'cpf', 'name', 'password', 'confirm_password', 'date_joined']
        read_only_fields = ['date_joined']

    def validate(self, data):
        # Valida se as senhas coincidem
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "As senhas não coincidem."})
        
        # Valida os campos personalizados
        self.validate_name(data['name'])
        self.validate_email(data['email'])
        self.validate_cpf(data['cpf'])
        
        return data

    def create(self, validated_data):
        """
        Remove o campo 'confirm_password' antes de criar o usuário.
        """
        validated_data.pop(
            'confirm_password')  # Remover o campo 'confirm_password'
        return Usuario.objects.create_user(**validated_data)


    def validate_db(self, attrs):
        """
        Verifica se já existe um registro com os mesmos nome, CPF e email.
        """
        cpf = attrs.get('cpf')
        email = attrs.get('email')

        # Checa se já existe um registro com os mesmos dados
        if Usuario.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError(
                "Já existe um registro com os mesmos CPF."
            )
        
        elif Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                "Já existe um registro com os mesmos Email."
            )
        return attrs

    def validate_name(self, value):
        # Valida um nome usando regex. Deve conter apenas letras e espaços.
        if not re.fullmatch(r'^[A-Za-zÀ-ÿ\s]+$', value):
            raise ValidationError(
                "O nome deve conter apenas letras e espaços.")
        return value

    def validate_email(self, value):
        # Valida um email usando regex.
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.fullmatch(email_regex, value):
            raise ValidationError("O email fornecido é inválido.")
        return value

    def validate_cpf(self, cpf):
        """
        Valida um CPF usando regex e os dígitos verificadores.
        Levanta uma ValidationError se inválido.
        """
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))

        # Verifica se está no formato correto com 11 dígitos
        if not re.fullmatch(r'^\d{11}$', cpf):
            raise ValidationError("CPF deve conter 11 dígitos numéricos.")

        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * len(cpf):
            raise ValidationError("CPF inválido.")

        # Calcula o primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10 % 11) % 10

        # Calcula o segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10 % 11) % 10

        # Verifica se os dígitos calculados são iguais aos do CPF
        if cpf[-2:] != f"{digito1}{digito2}":
            raise ValidationError("CPF inválido.")
        return cpf


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Pode ser email ou CPF
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        # Definir se é e-mail ou CPF
        if "@" in identifier:
            lookup_field = "email"
        elif identifier.isdigit() and len(identifier) in [11, 14]:  # CPF
            lookup_field = "cpf"
        else:
            raise serializers.ValidationError(
                "Informe um email ou CPF válido.")

        # Buscar usuário
        try:
            user = User.objects.get(**{lookup_field: identifier})
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciais inválidas.")

        # Verificar se está bloqueado
        if user.is_locked():
            raise serializers.ValidationError(
                "Muitas tentativas. Tente novamente mais tarde.")

        # Verificar senha
        if not user.check_password(password):
            user.increment_login_attempts()  # Registra tentativa falha
            raise serializers.ValidationError("Credenciais inválidas.")

        # Resetar tentativas se o login for bem-sucedido
        user.reset_login_attempts()

        # Adicionar usuário aos dados validados
        attrs["user"] = user
        return attrs
