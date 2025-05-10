import requests
from django.conf import settings
import logging

logger = logging.getLogger('django')


class ZeroOneGateway:
    @staticmethod
    def generate_pix_payment(payload):
        headers = {
            'Authorization': settings.ZEROONE_SECRET_KEY,
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
