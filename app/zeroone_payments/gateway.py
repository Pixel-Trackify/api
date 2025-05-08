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
            logger.debug("Enviando requisição ao gateway ZeroOne...")
            logger.debug(f"URL: {settings.ZEROONE_API_URL}")
            logger.debug(f"Headers: {headers}")
            logger.debug(f"Payload: {payload}")

            response = requests.post(
                settings.ZEROONE_API_URL, json=payload, headers=headers)

            logger.debug(f"Status Code: {response.status_code}")
            logger.debug(f"Resposta do Gateway: {response.text}")

            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")
            raise Exception(
                f"Erro ao comunicar com o gateway ZeroOne: {str(e)}")
