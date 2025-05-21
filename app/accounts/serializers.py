import socket
import re
from custom_admin.models import Configuration
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.utils.html import strip_tags
import html
from accounts.models import Usuario
from django.conf import settings
from payments.models import UserSubscription
from django.utils import timezone
from datetime import timedelta
import uuid


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    captcha = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Usuario
        fields = ['uid', 'email', 'cpf', 'name', 'password',
                  'confirm_password', 'date_joined', 'avatar', 'captcha']
        read_only_fields = ['date_joined']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"password": "As senhas não coincidem."})

         # Valida a senha usando o PasswordValidator
        password_validator = PasswordValidator()
        password_validator(data['password'])

        cpf = data.get('cpf')
        if cpf and not CPFValidator.validar_cpf(cpf):
            raise serializers.ValidationError({"cpf": "CPF inválido."})

        # Valida o captcha se necessário
        config = Configuration.objects.first()
        if config and config.recaptchar_enable and not data.get('captcha'):
            raise serializers.ValidationError(
                {'captcha': 'Este campo é obrigatório.'})
        return data

    def create(self, validated_data):
        # Remove o campo extra antes de criar o usuário
        validated_data.pop('confirm_password')

        user = Usuario.objects.create_user(**validated_data)
        avatar = validated_data.pop('avatar', None)
        if avatar:
            user.avatar = avatar
            user.save()

        config = Configuration.objects.first()
        if config and config.require_email_confirmation:
            user.is_active = False
            user.save()

        else:
            user.is_active = True
            user.save()

        return user

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


class CPFValidator:
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
        self.require_uppercase = settings.PASSWORD_REQUIRE_UPPERCASE
        self.require_special_char = settings.PASSWORD_REQUIRE_SPECIAL_CHAR

    def validate_length(self, password):
        if len(password) < self.min_length:
            raise serializers.ValidationError(
                {"password": f"A senha deve ter no mínimo {self.min_length} caracteres."}
            )
        if len(password) > self.max_length:
            raise serializers.ValidationError(
                {"password": f"A senha deve ter no máximo {self.max_length} caracteres."}
            )

    def validate_uppercase(self, password):
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            raise ValidationError(
                {"password": "A senha deve conter pelo menos 1 letra maiúscula."}
            )

    def validate_special_char(self, password):
        if self.require_special_char and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                {"password": "A senha deve conter pelo menos 1 caractere especial."}
            )

    def __call__(self, password):
        self.validate_length(password)
        self.validate_uppercase(password)
        self.validate_special_char(password)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False)  # Campo opcional

    class Meta:
        model = Usuario
        fields = ['name', 'email', 'password', 'account_type']
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
            raise serializers.ValidationError(
                {"message": "Informe um email ou CPF válido."})

        try:
            user = User.objects.get(**{lookup_field: identifier})
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"message": "As credenciais fornecidas estão incorretas. Verifique e tente novamente."})

        # Sempre verifica a senha, mesmo que o usuário esteja bloqueado
        correct_password = user.check_password(password)

        if correct_password:
            # Se a senha estiver correta, resetamos o bloqueio e as tentativas
            user.reset_login_attempts()
        else:
            # Se a senha estiver errada e o usuário já estiver bloqueado, mantém o bloqueio
            if user.is_locked():
                raise serializers.ValidationError(
                    {"message": "Muitas tentativas. Tente novamente mais tarde."})

            # Incrementa as tentativas e bloqueia se necessário
            user.increment_login_attempts()
            raise serializers.ValidationError(
                {"message": "As credenciais fornecidas estão incorretas. Verifique e tente novamente."})

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Usuario
        fields = ['uid', 'name', 'email', 'cpf',
                  'avatar', 'date_joined', 'profit']

    def validate_name(self, value):

        try:
            value.encode('latin-1')
        except UnicodeEncodeError:
            raise serializers.ValidationError(
                "O campo só pode conter caracteres ASCII.")

        if html.unescape(strip_tags(value)) != value:
            raise serializers.ValidationError(
                "O campo não pode conter tags HTML.")

        if len(value) < 5:
            raise serializers.ValidationError(
                "O campo deve ter pelo menos 5 caracteres.")
        if len(value) > 100:
            raise serializers.ValidationError(
                "O campo não pode exceder 100 caracteres.")

        return value

    def validate(self, data):
        """
        Valida os dados enviados no PUT.
        """
        cpf = data.get('cpf')
        if cpf:
            if not CPFValidator.validar_cpf(cpf):
                raise serializers.ValidationError({"cpf": "CPF inválido."})

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer para alterar a senha do usuário.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Senha antiga incorreta.")
        return value

    def validate(self, data):
        new_password = data.get('new_password')
        confirm_new_password = data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError(
                {"confirm_new_password": "As senhas não coincidem."})

        password_validator = PasswordValidator()
        password_validator(new_password)

        return data


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    change_password = serializers.BooleanField(
        write_only=True, required=False, default=False)
    admin = serializers.BooleanField(required=False, default=False)
    cpf = serializers.CharField(required=False)  # Campo para CPF

    class Meta:
        model = Usuario
        fields = ['name', 'email', 'cpf', 'password',
                  'confirm_password', 'change_password', 'admin']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate_cpf(self, value):
        """
        Valida o CPF para garantir que ele seja único e válido.
        """
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError(
                "O CPF deve conter 11 dígitos numéricos.")
        if Usuario.objects.filter(cpf=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Este CPF já está em uso.")
        return value

    def validate(self, data):
        """
        Valida os dados do serializer.
        """
        if not data:
            raise serializers.ValidationError(
                "Nenhum dado foi enviado para atualização.")

        if data.get('change_password'):
            if not data.get('password') or not data.get('confirm_password'):
                raise serializers.ValidationError(
                    "Os campos 'password' e 'confirm_password' são obrigatórios ao alterar a senha."
                )
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError(
                    "Os campos 'password' e 'confirm_password' devem ser iguais."
                )
        return data

    def update(self, instance, validated_data):
        """
        Atualiza os dados do usuário.
        """
        admin_flag = validated_data.pop('admin', None)
        if admin_flag is not None:
            instance.is_superuser = admin_flag

        if validated_data.pop('change_password', False):
            password = validated_data.pop('password', None)
            if password:
                instance.set_password(password)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class MultipleDeleteSerializer(serializers.Serializer):
    uids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Lista de UIDs dos usuários a serem excluídos."
    )
