from rest_framework import serializers
from plans.models import Plan
from .models import SubscriptionPayment, UserSubscription


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


class PlanInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["uid", "name", "price", "duration", "duration_value"]


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="plan.name")
    price = serializers.FloatField(source="plan.price")
    duration = serializers.CharField(source="plan.duration")
    duration_value = serializers.CharField(source="plan.duration_value")
    uid = serializers.UUIDField(source="plan.uid")
    method = serializers.SerializerMethodField()
    expiration = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserSubscription
        fields = ["uid", "name", "price", "status", "method",
                  "duration", "duration_value", "expiration"]

    def get_method(self, obj):
        last_payment = SubscriptionPayment.objects.filter(
            subscription=obj).order_by('-created_at').first()
        return last_payment.payment_method if last_payment else None


class PaymentOpenedSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(
        source="created_at", format="%Y-%m-%d %H:%M:%S")
    amount = serializers.FloatField(source="price")

    class Meta:
        model = SubscriptionPayment
        fields = ["uid", "amount", "date"]


class PaymentHistoricSerializer(serializers.ModelSerializer):
    data = serializers.DateTimeField(
        source="created_at", format="%Y-%m-%d %H:%M:%S")
    amount = serializers.FloatField(source="price")

    class Meta:
        model = SubscriptionPayment
        fields = ["uid", "amount", "status", "data"]
