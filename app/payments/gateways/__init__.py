from .zeroone import ZeroOneGateway
from .firebanking import FirebankingGateway
import logging
logger = logging.getLogger('django')


def get_gateway(gateway_name):
    """
    Retorna a instância do gateway de pagamento conforme o nome informado.
    """
    logger.info(f"Obtendo gateway de pagamento: {gateway_name}")
    if gateway_name == 'zeroone':
        return ZeroOneGateway()
    elif gateway_name == 'firebanking':
        return FirebankingGateway()
    else:
        raise ValueError(f"Gateway '{gateway_name}' não suportado.")
