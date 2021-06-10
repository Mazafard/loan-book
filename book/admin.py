from django.contrib import admin

from .models import (
    Book,
    BookLoanHistory,
    Genre)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('title',)
    fields = ('title',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fields = ('title', 'author', 'genre', 'prerequisite')

    list_display = ('title', 'author', 'genre', 'state')
    search_fields = ['title', 'author']
    list_filter = ['genre__title', 'author']


@admin.register(BookLoanHistory)
class BookRentHistoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'customer', 'loan_request_date', 'back_date', 'state')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
