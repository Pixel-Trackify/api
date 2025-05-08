from rest_framework import serializers
from plans.models import Plan


class PaymentSerializer(serializers.Serializer):

    paymentMethod = serializers.ChoiceField(
        choices=['PIX', 'CREDIT_CARD', 'DEBIT_CARD', 'BOLETO']
    )
    plan_uid = serializers.UUIDField()

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
