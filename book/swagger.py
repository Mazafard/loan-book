from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from book.serializers import *
# ==================================
#     Accounting API Responses
# ==================================
from common.pagination import PageNumberPagination

BookList_GET = {
    status.HTTP_200_OK: BookSerializer(),
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
    status.HTTP_404_NOT_FOUND: 'Information not found',
}

BookDetail_GET = {
    status.HTTP_200_OK: BookSingleSerializer(),
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
    status.HTTP_404_NOT_FOUND: 'Requested tenant not found',
}

BOOK_LOAN_PUT = {
    status.HTTP_204_NO_CONTENT: '',
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
    status.HTTP_404_NOT_FOUND: 'Information not found',
}
BOOK_LOAN_DELETE = {
    status.HTTP_204_NO_CONTENT: '',
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
    status.HTTP_404_NOT_FOUND: 'Information not found',
}
# ==================================
#    Book API Parameters
# ==================================
BOOK_SEARCH = openapi.Parameter(
    name='search', in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Search in title & genre & author book',
)

BOOK_FILTER_STATE = openapi.Parameter(
    name='filter_state', in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Filter books by state',
)

BOOK_FILTER_AUTHOR = openapi.Parameter(
    name='filter_author', in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Filter books by author',
)

BOOK_FILTER_GENRE_TITLE = openapi.Parameter(
    name='filter_genre_title', in_=openapi.IN_QUERY,
    type=openapi.TYPE_STRING,
    description='Filter books by genre title',
)

# ==================================
#     Tenant Swagger Decorators
# ==================================
book_list = swagger_auto_schema(
    operation_description='List books',
    responses=BookList_GET,
    manual_parameters=[
        BOOK_SEARCH,
        BOOK_FILTER_STATE,
        BOOK_FILTER_AUTHOR,
        BOOK_FILTER_GENRE_TITLE,
    ],
    PaginatorInspector=[PageNumberPagination]

)
book_retrieve = swagger_auto_schema(operation_description='Retrieve Book', responses=BookDetail_GET)

book_loan = swagger_auto_schema(
    operation_description='loan Book',
    responses=BOOK_LOAN_PUT,
)

book_back = swagger_auto_schema(
    operation_description='back Book',
    responses=BOOK_LOAN_DELETE
)
