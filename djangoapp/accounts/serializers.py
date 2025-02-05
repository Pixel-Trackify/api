import socket
import re
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Usuario
from django.conf import settings



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'cpf', 'name',
                  'password', 'confirm_password', 'date_joined']
        read_only_fields = ['date_joined']

    def validate(self, data):
            # Valida se as senhas coincidem
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "As senhas não coincidem."})

        # Valida senha com as regras definidas no PasswordValidator
        password_validator = PasswordValidator()
        try:
            password_validator(data['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        # Valida se CPF e email já existem no banco
        self.validate_db(data)

        return data
    def create(self, validated_data):
        """
        Remove o campo 'confirm_password' antes de criar o usuário.
        """
        validated_data.pop('confirm_password')
        return Usuario.objects.create_user(**validated_data)

    def validate_db(self, attrs):
        """
        Verifica se já existe um registro com o mesmo CPF ou email.
        """
        cpf = attrs.get('cpf')
        email = attrs.get('email')

        if Usuario.objects.filter(cpf=cpf).exists():
            raise serializers.ValidationError({"cpf": "CPF já está em uso."})

        if Usuario.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "Email já está em uso."})

        return attrs

    def validate_name(self, value):
        """
        Valida um nome usando regex. Deve conter apenas letras e espaços.
        """
        if not re.fullmatch(r'^[A-Za-zÀ-ÿ\s]+$', value):
            raise serializers.ValidationError(
                "O nome deve conter apenas letras e espaços.")
        return value

    def validate_email(self, email):
        """
        Valida um email verificando:
        - Tamanho adequado
        - Formato correto
        - Domínio válido
        """
        if len(email) > 100:
            raise serializers.ValidationError("O email é muito longo.")
        if len(email) < 5:
            raise serializers.ValidationError("O email é muito curto.")

        # Validar formato de email
        email_regex = r"^[a-zA-Z0-9_.+-]+@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)$"
        match = re.match(email_regex, email)
        if not match:
            raise serializers.ValidationError("Formato de email inválido.")

        # Validar domínio
        dominio = match.group(1)
        try:
            socket.getaddrinfo(dominio, None)
        except socket.gaierror:
            raise serializers.ValidationError(
                "O provedor de email não é válido.")

        return email

    def validate_cpf(self, cpf):
        """
        Valida se o CPF informado é válido.
        """
        if not self.validar_cpf(cpf):
            raise serializers.ValidationError("CPF inválido.")
        return cpf

    
    @staticmethod
    def validar_cpf(cpf):
        # Remove todos os caracteres não numéricos
        cpf = re.sub(r'\D', '', cpf)

        # Verifica se tem 11 dígitos ou se todos são iguais
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        # Cálculo do primeiro dígito verificador
        soma = 0
        multiplicador = 10
        for digito in cpf[:9]:
            soma += int(digito) * multiplicador
            multiplicador -= 1
        resto = (soma * 10) % 11
        digito_1 = resto if resto < 10 else 0

        # Cálculo do segundo dígito verificador
        soma = 0
        multiplicador = 11
        for digito in cpf[:10]:
            soma += int(digito) * multiplicador
            multiplicador -= 1
        resto = (soma * 10) % 11
        digito_2 = resto if resto < 10 else 0

        # Valida os dígitos verificadores
        return cpf[-2:] == f"{digito_1}{digito_2}"




class PasswordValidator:
    """
    Validador completo com todas as regras configuráveis via .env
    """

    def __init__(self):
        self.min_length = settings.PASSWORD_MIN
        self.max_length = settings.PASSWORD_MAX
        self.block_common = settings.PASSWORD_BLOCK_COMMON
        self.common_passwords = self.load_common_passwords()
        self.require_uppercase = settings.PASSWORD_REQUIRE_UPPERCASE
        self.require_special_char = settings.PASSWORD_REQUIRE_SPECIAL_CHAR

    def load_common_passwords(self):
        if not self.block_common:
            return set()

        try:
            with open(settings.PASSWORD_COMMON_LIST, 'r') as f:
                return {line.strip().lower() for line in f}
        except FileNotFoundError:
            return set()

    def validate_length(self, password):
        if len(password) < self.min_length:
            raise ValidationError(
                f"A senha deve ter no mínimo {self.min_length} caracteres.")
        if len(password) > self.max_length:
            raise ValidationError(
                f"A senha deve ter no máximo {self.max_length} caracteres.")

    def validate_uppercase(self, password):
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError(
                "A senha deve conter pelo menos 1 letra maiúscula.")

    def validate_special_char(self, password):
        if self.require_special_char and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                "A senha deve conter pelo menos 1 caractere especial.")

    def validate_common_password(self, password):
        if password.lower() in self.common_passwords:
            raise ValidationError(
                "Essa senha é muito comum e insegura. Escolha outra.")

    def __call__(self, password):
        self.validate_length(password)
        self.validate_uppercase(password)
        self.validate_special_char(password)
        self.validate_common_password(password)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False)  # Campo opcional

    class Meta:
        model = Usuario
        fields = ['name', 'email', 'password']
        extra_kwargs = {
            'email': {'required': False},  # Permite atualização sem email
            'name': {'required': False},
        }

    def update(self, instance, validated_data):
        # Atualiza password se fornecido
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Pode ser email ou CPF
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if "@" in identifier:
            lookup_field = "email"
        elif identifier.isdigit() and len(identifier) in [11, 14]:  # CPF
            lookup_field = "cpf"
        else:
            raise serializers.ValidationError("Informe um email ou CPF válido.")

        try:
            user = User.objects.get(**{lookup_field: identifier})
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciais inválidas.")

        # Verificar se está bloqueado
        if user.is_locked():
            raise serializers.ValidationError(
                "Muitas tentativas. Tente mais tarde.")

        # Verificar senha
        if not user.check_password(password):
            user.increment_login_attempts()  # Registra tentativa falha
            raise serializers.ValidationError("Credenciais inválidas.")

        # Limpa todos os dados de bloqueio se a senha estiver correta
        user.reset_login_attempts()

        # Atualiza a instância do banco para refletir os dados atualizados
        user.refresh_from_db()

        attrs["user"] = user
        return attrs


'''class LoginSerializer(serializers.Serializer):
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
'''