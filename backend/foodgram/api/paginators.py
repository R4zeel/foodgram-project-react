from rest_framework.pagination import PageNumberPagination


class LimitParamPagination(PageNumberPagination):
    page_size_query_param = 'limit'
