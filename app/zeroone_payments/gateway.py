from custom_admin.models import Configuration
import requests
from django.conf import settings
import logging

logger = logging.getLogger('django')


class ZeroOneGateway:
    @staticmethod
    def generate_pix_payment(payload):
        config = Configuration.objects.first()
        if not config or not config.zeroone_secret_key:
            raise Exception("Chave ZeroOne não encontrada.")
        zeroone_secret_key = config.zeroone_secret_key

        headers = {
            'Authorization': zeroone_secret_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                settings.ZEROONE_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")
