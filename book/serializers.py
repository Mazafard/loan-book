from django.contrib.auth.models import AnonymousUser
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from book.models import Book, Genre, BookLoanHistory
from common.serializers import BaseModelSerializer
from users.models import Customer


class GenreSerializer(BaseModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'id',
            'title',
        )


class BookLoanHistorySerializer(BaseModelSerializer):
    class Meta:
        model = BookLoanHistory
        fields = ('loan_request_date', 'id', 'back_date', 'state')


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class SubBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            'title',
            'genre',
            'state',

        )


class BookSerializer(BaseModelSerializer):
    genre = GenreSerializer()
    loan_status = serializers.SerializerMethodField()
    prerequisite = SubBookSerializer(many=True)

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'genre',
            'state',
            'prerequisite',
            'loan_status'
        )

    @swagger_serializer_method(serializer_or_field=BookLoanHistorySerializer)
    def get_loan_status(self, obj):
        request = self.context.get('request', None)
        if not request or \
                isinstance(request.user, AnonymousUser) or \
                not hasattr(request, 'user') or \
                not isinstance(request.user, Customer):
            return None

        loan_history = request.user.get_loans().filter(
            book=obj,
        ).first()
        if not loan_history:
            return None

        return BookLoanHistorySerializer(loan_history).data


class BookSingleSerializer(BaseModelSerializer):
    genre = GenreSerializer()
    prerequisite = BookSerializer(many=True)
    loan_status = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'genre',
            'state',
            'prerequisite',
            'loan_status'
        )

    @swagger_serializer_method(serializer_or_field=BookLoanHistorySerializer)
    def get_loan_status(self, obj):
        request = self.context.get('request', None)
        if not request or \
                isinstance(request.user, AnonymousUser) or \
                not hasattr(request, 'user') or \
                not isinstance(request.user, Customer):
            return None

        loan_history = request.user.get_loans().filter(
            book=obj,
        ).first()
        if not loan_history:
            return None

        return BookLoanHistorySerializer(loan_history).data
