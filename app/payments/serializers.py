from rest_framework import serializers
from django.utils.timezone import now
from plans.models import Plan, PlanFeature
from .models import SubscriptionPayment, UserSubscription
from custom_admin.models import Configuration
from decimal import Decimal


class PaymentSerializer(serializers.Serializer):
    paymentMethod = serializers.ChoiceField(
        choices=['PIX', 'CREDIT_CARD', 'DEBIT_CARD', 'BOLETO']
    )
    plan_uid = serializers.UUIDField()
    gateway = serializers.ChoiceField(
        choices=[('zeroone', 'ZeroOne'), ('firebanking', 'Firebanking')]
    )

    class Meta:
        model = SubscriptionPayment
        fields = [
            'uid', 'idempotency', 'payment_method', 'gateway', 'token',
            'price', 'gateway_response', 'status', 'subscription', 'created_at'
        ]
    read_only_fields = [
        'uid', 'idempotency', 'token', 'gateway_response', 'status', 'created_at', 'subscription', 'price'
    ]

    def validate(self, data):
        """
        Valida os dados de entrada e preenche os campos automaticamente.
        """

        try:
            plan = Plan.objects.get(uid=data['plan_uid'])
            data['plan'] = plan
        except Plan.DoesNotExist:
            raise serializers.ValidationError(
                {"plan_uid": "Plano não encontrado."})

        data['amount'] = int(plan.price * 100)

        data['items'] = [
            {
                "unitPrice": int(plan.price * 100),
                "plan_uid": str(plan.uid),
                "quantity": 1,
                "tangible": False
            }
        ]

        return data


class PlanFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanFeature
        fields = ["text", "active"]


class PlanInfoSerializer(serializers.ModelSerializer):
    features = PlanFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ["uid", "name", "price",
                  "duration", "duration_value", "features", "integration_limit", "campaign_limit", "kwai_limit"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="plan.name")
    price = serializers.FloatField(source="plan.price")
    duration = serializers.CharField(source="plan.duration")
    duration_value = serializers.CharField(source="plan.duration_value")
    uid = serializers.UUIDField(source="plan.uid")
    method = serializers.SerializerMethodField()
    expiration = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    integration_limit = serializers.IntegerField(
        source="plan.integration_limit", read_only=True)
    campaign_limit = serializers.IntegerField(
        source="plan.campaign_limit", read_only=True)
    kwai_limit = serializers.IntegerField(
        source="plan.kwai_limit", read_only=True)

    class Meta:
        model = UserSubscription
        fields = ["uid", "name", "price", "status", "method",
                  "duration", "duration_value", "expiration", "integration_limit", "campaign_limit", "kwai_limit"]

    def get_method(self, obj):
        last_payment = SubscriptionPayment.objects.filter(
            subscription=obj).order_by('-created_at').first()
        return last_payment.payment_method if last_payment else None


class PaymentOpenedSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        source="created_at", format="%Y-%m-%d %H:%M:%S")
    amount = serializers.FloatField(source="price")
    tax = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPayment
        fields = ["uid", "amount", "date", "tax", "total"]

    def get_tax(self, obj):
        config = Configuration.objects.first()
        late_interest = config.late_payment_interest or 0
        daily_late_interest = config.daily_late_payment_interest or 0

        if not obj.subscription or not obj.subscription.expiration:
            return "0.00"

        expiration_date = obj.subscription.expiration.date() if hasattr(
            obj.subscription.expiration, 'date') else obj.subscription.expiration
        today = now().date()
        price = Decimal(obj.price)
        tax = Decimal('0.00')

        if expiration_date < today and (late_interest > 0 or daily_late_interest > 0):
            juros = Decimal('0.00')
            if late_interest > 0:
                juros = (Decimal(str(late_interest)) / Decimal('100')) * price
            dias_atraso = (today - expiration_date).days
            juros_diario = Decimal('0.00')
            if daily_late_interest > 0:
                juros_diario = (Decimal(str(daily_late_interest)) /
                                Decimal('100')) * price * dias_atraso
            tax = juros + juros_diario

        return str(tax.quantize(Decimal('0.01')))

    def get_total(self, obj):
        price = Decimal(obj.price)
        tax = Decimal(self.get_tax(obj))
        return str((price + tax).quantize(Decimal('0.01')))


class PaymentHistoricSerializer(serializers.ModelSerializer):
    data = serializers.DateTimeField(
        source="created_at", format="%Y-%m-%d %H:%M:%S")
    amount = serializers.FloatField(source="price")

    class Meta:
        model = SubscriptionPayment
        fields = ["uid", "amount", "status", "data"]
