from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    page_size = 10  # Número padrão de itens por página
    page_size_query_param = 'page_size'  # Permite alterar o tamanho da página via parâmetro
    max_page_size = 100  # Limite máximo de itens por página
    page_query_param = 'page'  # Nome do parâmetro para a página