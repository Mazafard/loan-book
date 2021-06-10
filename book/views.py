from django.utils.decorators import method_decorator
from django_fsm import can_proceed
from rest_framework import status

from common.auth import JWTTokenAuthentication
from common.permissions import IsAuthenticatedCustomer
from common.response import ErrorResponse, Response
from common.views import PaginatedViewSet
from . import serializers, errors
from .models import (
    Book,
    BookLoanHistory,
)
from .swagger import book_list, book_retrieve, book_back, book_loan


class BookView(PaginatedViewSet):
    authentication_classes = (JWTTokenAuthentication,)
    permission_classes = [IsAuthenticatedCustomer, ]
    serializer_class = serializers.BookSerializer
    single_serializer_class = serializers.BookSingleSerializer

    def get_queryset(self, request):
        return Book.get_all()

    @method_decorator(name='list', decorator=book_list)
    def list(self, request):
        return super().list(request)

    @method_decorator(name='retrieve', decorator=book_retrieve)
    def retrieve(self, request, pk=None):
        if not BookLoanHistory.objects.filter(book__id=pk, state='loaned', customer__id=request.user.pk).exists():
            return self.not_found(request)
        return super().retrieve(request, pk)

    @method_decorator(name='loan', decorator=book_loan)
    def loan(self, request, pk):
        book = self.get_object(request, pk)  # type: Book
        if not book:
            return ErrorResponse(errors.THERE_IS_NOT_ANY_BOOK)

        book_loan_history, _ = BookLoanHistory.objects.get_or_create(
            customer=request.user,
            book=book,
            defaults={
                'customer': request.user,
                'book': book,

            }
        )

        if not can_proceed(book_loan_history.loan):
            return ErrorResponse(
                errors.THE_BOOK_IS_NOT_RELEASED,
                errors=f" book status is {book.state} "
                       f"and current user loan history status is {book_loan_history.state} "
                       f"and user prerequisite is {book_loan_history.has_prerequisite_permission()}"

            )
        book_loan_history.loan()
        book_loan_history.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @method_decorator(name='back', decorator=book_back)
    def back(self, request, pk):
        book = self.get_object(request, pk)  # type: Book
        if not book:
            return ErrorResponse(errors.THERE_IS_NOT_ANY_BOOK)
        book_loan_history, _ = BookLoanHistory.objects.get_or_create(
            customer=request.user,
            book=book,
            defaults={
                'customer': request.user,
                'book': book,
            }
        )
        if not can_proceed(book_loan_history.back):
            return ErrorResponse(
                errors.THE_BOOK_IS_RELEASED,
                errors=f" book status is {book.state} and current user loan history status"
                       f" is {book_loan_history.state}"
            )
        book_loan_history.back()
        book_loan_history.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
