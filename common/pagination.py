import copy
import math
from abc import abstractmethod

from django.db import models
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination as DefaultPageNumberPagination

from common.response import Response


class PaginationFilterable:
    @classmethod
    @abstractmethod
    def get_filterable_fields(cls):
        return []


class PaginationSortable:
    @classmethod
    @abstractmethod
    def get_sortable_fields(cls):
        return []


class PaginationSearchable:
    @classmethod
    @abstractmethod
    def get_searchable_fields(cls):
        return []


class PageNumberPagination(object):
    FILTERABLE_KEY_MAP = {
        "filter__": "__icontains",
        "exact__": "",
        "lt__": "__lt",
        "lte__": "__lte",
        "gt__": "__gt",
        "gte__": "__gte",
    }

    def __init__(self, query_set, request, page_size=20, filterable_fields=None,
                 sortable_fields=None,
                 search_fields=None):
        """
        :param django.db.models.QuerySet query_set:
        :param rest_framework.request.Request request:
        :param int page_size:
        :param list filterable_fields:
        :param list sortable_fields:
        """

        self.filterable_fields = filterable_fields
        self.sortable_fields = sortable_fields
        self.search_fields = search_fields
        self._request = request
        self.current_page = int(request.query_params.get('page', 1)) if int(
            request.query_params.get('page', 1)) > 0 else 1

        self.search_text = self._request.query_params.get('search', None)
        self.query_set = query_set
        self._update_query_set()
        self.total_count = self.query_set.count()

        try:
            self.page_size = int(
                self._request.query_params.get('page_size', page_size))
        except ValueError as e:
            self.page_size = page_size

        self.page_count = int(math.ceil(
            self.total_count / self.page_size)) if self.page_size > 0 else 1

    def _update_query_set(self):
        if self.filterable_fields is None and issubclass(self.query_set.model,
                                                         PaginationFilterable):
            self.filterable_fields = self.query_set.model.get_filterable_fields()

        if self.sortable_fields is None and issubclass(self.query_set.model,
                                                       PaginationSortable):
            self.sortable_fields = self.query_set.model.get_sortable_fields()

        if self.search_fields is None and issubclass(self.query_set.model,
                                                     PaginationSearchable):
            self.search_fields = self.query_set.model.get_searchable_fields()

        if self.filterable_fields is None:
            self.filterable_fields = []

        if self.sortable_fields is None:
            self.sortable_fields = []

        if self.search_fields is None:
            self.search_fields = []

        for value in self._get_filter_kwargs_list():
            self.query_set = self.query_set.filter(**value)

        if self.search_text:
            or_query = None
            for field in self.search_fields:
                q = Q(**{'{}__icontains'.format(field):
                             self._get_value(field, self.search_text)}
                      )
                if or_query:
                    or_query = or_query | q
                else:
                    or_query = q
            if or_query:
                self.query_set = self.query_set.filter(or_query)

        for value in self._get_sort_list():
            self.query_set = self.query_set.order_by(value)

    def _get_filter_kwargs_list(self):
        for key, value in self._request.query_params.items():
            if key in self.filterable_fields:
                if hasattr(self.query_set.model, key):
                    query_kwarg = getattr(self.query_set.model, key)(value)
                    if isinstance(query_kwarg, dict):
                        yield query_kwarg
                    continue

            for k, v in self.FILTERABLE_KEY_MAP.items():
                if key.startswith(k):
                    new_key = key.replace(k, "", 1)
                    if new_key in self.filterable_fields:
                        yield {
                            "{}{}".format(new_key, v): self._get_value(new_key,
                                                                       value)
                        }

    def _get_value(self, key, value, model=None):

        meta = model._meta if model else self.query_set.model._meta
        split_ket = key.split('__', 1)
        if len(split_ket) > 1:
            model = meta.get_field(split_ket[0]).related_model
            return self._get_value(split_ket[1], value, model)

        field = meta.get_field(key)

        if value == 'null':
            return None

        if isinstance(field, (models.CharField, models.TextField)):
            return self._arabic_to_persian(str(value))

        if isinstance(field, models.BooleanField):
            if value.lower() == "false" or value == "0":
                return False
            return True

        if isinstance(field, (
                models.IntegerField, models.BigIntegerField,
                models.BigAutoField)):
            try:
                return int(value)
            except ValueError as e:
                return 0

        if isinstance(field, (models.FloatField, models.DecimalField)):
            try:
                return float(value)
            except ValueError as e:
                return 0.0

        return value

    def _arabic_to_persian(self, word):
        characters = {
            'ك': 'ک',
            'دِ': 'د',
            'بِ': 'ب',
            'زِ': 'ز',
            'ذِ': 'ذ',
            'شِ': 'ش',
            'سِ': 'س',
            'ى': 'ی',
            'ي': 'ی',
            '١': '۱',
            '٢': '۲',
            '٣': '۳',
            '٤': '۴',
            '٥': '۵',
            '٦': '۶',
            '٧': '۷',
            '٨': '۸',
            '٩': '۹',
            '٠': '۰',
        }
        for k, v in characters.items():
            word = word.replace(k, v)
        return word

    def _get_sort_list(self):
        sort_field = []

        request_sort = self._request.query_params.get('sort')
        if not request_sort:
            return sort_field

        for item in request_sort.split(","):
            if item.replace("-", "", 1).replace("+", "",
                                                1) in self.sortable_fields:
                yield item

    def get_result(self):
        if self.page_size > 0:
            return self.query_set[(
                                          self.current_page - 1) * self.page_size:self.page_size * self.current_page]
        return self.query_set.all()

    def get_total_count(self):
        return self.total_count

    def get_last_page(self):
        return self.page_count if self.page_count > 0 else 1

    def has_next_page(self):
        return self.current_page < self.get_last_page()

    def has_prev_page(self):
        return self.current_page > 1

    def get_next_page(self):
        if self.has_next_page():
            return self.current_page + 1

    def get_prev_page(self):
        if self.has_prev_page():
            return self.current_page - 1

    def get_first_page(self):
        return 1

    def get_pagination_headers(self):
        return {
            "X-Pagination-Total-Count": self.get_total_count(),
            "X-Pagination-Page-Count": self.get_last_page(),
            "X-Pagination-Current-Page": self.current_page,
            "X-Pagination-Per-Page": self.page_size,
            "X-Pagination-Sortable-Fields": ",".join(self.sortable_fields),
            "X-Pagination-Filterable-Fields": ",".join(self.filterable_fields),
            "X-Pagination-Searchable-Fields": ",".join(self.search_fields),
            "Link": self.get_links()
        }

    def get_links(self):

        url = "{0}://{1}{2}".format(
            self._request.scheme,
            self._request.get_host(),
            self._request.path,
        )

        def get_link(data):
            query_params = copy.copy(self._request.query_params)
            query_params._mutable = True
            query_params['page'] = data['page_number']
            return "<{rout}?{query_params}>; rel={rel}".format(
                rout=url,
                query_params=query_params.urlencode(safe="/"),
                rel=data['rel']
            )

        links = [{
            "page_number": 1,
            "rel": "first",
        }]

        if self.has_prev_page():
            links.append({
                "page_number": self.get_prev_page(),
                "rel": "prev",
            })

        links.append({
            "page_number": self.current_page,
            "rel": "self",
        })

        if self.has_next_page():
            links.append({
                "page_number": self.get_next_page(),
                "rel": "next",
            })

        links.append({
            "page_number": self.get_last_page(),
            "rel": "last",
        })

        return ", ".join([get_link(link) for link in links])


class CustomPaginator(DefaultPageNumberPagination):
    def __init__(self, page_size):
        self.page_size = page_size

    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(query_set, request)

        except NotFound:
            return Response({"error": "No results found for the requested page"}, status=status.HTTP_400_BAD_REQUEST)

        serialized_page = serializer_obj(page_data, many=True)
        return self.get_paginated_response(serialized_page.data)
