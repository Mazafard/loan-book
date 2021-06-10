import datetime

from django.contrib.auth.models import User
from django.db import models
from django_fsm import FSMField, transition
from rest_framework.exceptions import NotFound

from common.models import BaseModel
from common.pagination import PaginationSearchable, PaginationSortable, PaginationFilterable
from users.models import Customer


######################################################################################################
# Genre Model ########################################################################################
######################################################################################################

class Genre(BaseModel):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Genres"


######################################################################################################
# Book Model #########################################################################################
######################################################################################################

class Book(BaseModel, PaginationSearchable, PaginationSortable, PaginationFilterable):
    prerequisite = models.ManyToManyField('self', related_name='prerequisites')
    title = models.CharField(max_length=300)
    author = models.CharField(max_length=100)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)
    state = FSMField(default='new', protected=True)

    ######################################################################################################
    # Transition loan stat ###############################################################################
    ######################################################################################################

    def book_is_not_under_loan(self):
        return not self.state == 'loaned'

    @transition(
        field=state,
        source=[
            'new',
            'released'
        ],
        target='loaned',
        conditions=[
            book_is_not_under_loan,
        ])
    def loan(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """

    ######################################################################################################
    # Transition back stats ##############################################################################
    ######################################################################################################

    def is_released(self):
        return self.state == 'released'

    def can_back(self):
        return not self.is_released()

    @transition(field=state, source='loaned', target='released', conditions=[can_back, ])
    def back(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Books"

    ######################################################################################################
    # Pagination & Sort & Filter #########################################################################
    ######################################################################################################
    @classmethod
    def get_searchable_fields(cls):
        return [
            'title',
            'author',
            'genre__title',
        ]

    @classmethod
    def get_sortable_fields(cls):
        return [
            'id',
            'created_at',
            'updated_at',

        ]

    @classmethod
    def get_filterable_fields(cls):
        return [
            'genre__title',
            'author',
            'state'
        ]

    ######################################################################################################
    # Class Methods  #########################################################################
    ######################################################################################################
    @classmethod
    def get_by_title(cls, title, raise_exception=False) -> 'Book':
        obj = cls.objects.filter(title=title).first()
        if raise_exception and not obj:
            raise NotFound('The requested Book is not found')
        return obj


######################################################################################################
# Book Loan History Model #################################################################################
######################################################################################################

class BookLoanHistory(BaseModel):
    book = models.ForeignKey(
        Book, on_delete=models.PROTECT, editable=False, related_name='loan_histories')
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, editable=False, related_name='loan_histories')
    loan_request_date = models.DateField(
        auto_now_add=True,
        editable=False,
        blank=True,
        null=True,
    )

    back_date = models.DateField(
        blank=True,
        null=True,
        editable=False
    )
    state = FSMField(default='new', protected=True)

    class Meta:
        verbose_name_plural = "Book Rent Histories"

    ######################################################################################################
    # Transition stats to loan ###########################################################################
    ######################################################################################################

    def user_has_prerequisite_permission(self):
        pr = self.book.prerequisite.values_list('id', flat=True)
        if not pr:
            return True
        user_pr = BookLoanHistory.objects.filter(
            customer_id=self.customer.pk,
            book_id__in=list(pr),
            state__exact='give_back'

        ).values_list('book_id', flat=True)
        if not set(pr) == set(user_pr):
            return False
        return True

    def book_is_not_under_loan(self):
        return not self.book.state == 'loaned'

    def user_does_not_loan_book(self):
        return not self.state == 'loaned'

    @transition(
        field=state,
        source='new',
        target='loaned',
        conditions=[
            user_does_not_loan_book,
            user_has_prerequisite_permission,
            book_is_not_under_loan
        ])
    def loan(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """
        self.rent_date = datetime.datetime.now()
        self.back_date = datetime.datetime.now() + datetime.timedelta(14)
        self.book.loan()
        self.book.save()
        self.save()

    ######################################################################################################
    # Transition stats to back ###########################################################################
    ######################################################################################################

    def can_back_current_user(self):
        return self.state == 'loaned'

    def is_not_released(self):
        return not self.book.state == 'released'

    def can_back(self):
        return self.can_back_current_user()

    @transition(
        field=state,
        source='loaned',
        target='give_back',
        conditions=[
            can_back,
            is_not_released,
            can_back_current_user,

        ])
    def back(self):
        """
        This function may contain side-effects,
        like updating caches, notifying users, etc.
        The return value will be discarded.
        """
        self.book.back()
        self.book.save()
        self.save()

######################################################################################################
