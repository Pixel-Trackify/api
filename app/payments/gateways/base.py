class PaymentGatewayBase:
    def generate_payment(self, user, plan, payment_method):
        raise NotImplementedError("Implemente este método na subclasse.")