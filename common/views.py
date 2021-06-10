from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from common import errors
from common.pagination import PageNumberPagination
from common.response import ErrorResponse, Response


class BaseAPIView(APIView):
    def http_method_not_allowed(self, request, *args, **kwargs):
        return ErrorResponse(errors.METHOD_NOT_ALLOWED)

    def handle_error(
            self,
            message=None,
            serializer_errors=None,
            status_code=status.HTTP_400_BAD_REQUEST,
            extra_data=None,
            code=None
    ):
        if serializer_errors is None:
            serializer_errors = []

        error = {
            "status_code": status_code,
            "code": code if code else status_code,
            "message": message if message else "The user request is not valid"
        }
        return ErrorResponse(
            error,
            errors=serializer_errors,
            extra_data=extra_data
        )

    def handle_exception(self, exc):
        if isinstance(exc, serializers.ValidationError):
            return self.handle_error(
                serializer_errors=exc.detail,
                status_code=exc.status_code,
            )

        if isinstance(exc, (
                exceptions.NotFound,
                exceptions.AuthenticationFailed,
                exceptions.PermissionDenied,
                exceptions.NotAuthenticated
        )):
            return self.handle_error(
                exc.detail,
                status_code=exc.status_code
            )

        if isinstance(exc, exceptions.Throttled):
            return self.handle_error(
                message=exc.detail,
                status_code=exc.status_code,
                extra_data={
                    "wait": exc.wait
                }
            )

        return super().handle_exception(exc)


class BaseViewSet(ViewSetMixin, BaseAPIView):
    queryset = None
    serializer_class = None
    single_serializer_class = None
    url_params = []

    @property
    def _single_serializer_class(self):
        return self.single_serializer_class if self.single_serializer_class \
            else self.serializer_class

    def has_update_permission(self, obj, request):
        return True

    def has_delete_permission(self, obj, request):
        return True

    def has_create_permission(self, request):
        return True

    def get_queryset(self, request):
        return self.queryset

    def handle_exception(self, exc):

        if isinstance(exc, NotFound):
            return self.not_found(self.request)

        return super().handle_exception(exc)

    def list(self, request):
        objects = self.get_queryset(request).all()
        return Response(data=self.serializer_class(
            objects,
            many=True,
            context=self.get_context(request)
        ).data)

    def create(self, request):
        if not self.has_create_permission(request):
            return self.no_create_permission(request)

        serializer = self._single_serializer_class(data=request.data,
                                                   context=self.get_context(
                                                       request))
        if not serializer.is_valid():
            return self.data_not_valid(request, serializer.errors)

        serializer.save(**self.create_default_params(request))
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self, request, pk=None):
        return self.get_queryset(request).filter(pk=pk).first()

    def retrieve(self, request, pk=None):
        obj = self.get_object(request, pk)
        if not obj:
            return self.not_found(request)

        return Response(
            data=self._single_serializer_class(obj,
                                               context=self.get_context(
                                                   request)).data)

    def update(self, request, pk=None):
        obj = self.get_object(request, pk)
        if not obj:
            return self.not_found(request)

        if not self.has_update_permission(obj, request):
            return self.no_update_permission(request)

        serializer = self._single_serializer_class(instance=obj,
                                                   data=request.data,
                                                   context=self.get_context(
                                                       request))
        if not serializer.is_valid():
            return self.data_not_valid(request, serializer.errors)

        serializer.save()
        return Response(data=serializer.data)

    def partial_update(self, request, pk=None):
        obj = self.get_object(request, pk)
        if not obj:
            return self.not_found(request)

        if not self.has_update_permission(obj, request):
            return self.no_update_permission(request)

        serializer = self._single_serializer_class(instance=obj,
                                                   data=request.data,
                                                   partial=True,
                                                   context=self.get_context(
                                                       request))
        if not serializer.is_valid():
            return self.data_not_valid(request, serializer.errors)

        serializer.save()
        return Response(data=serializer.data)

    def destroy(self, request, pk=None):
        obj = self.get_object(request, pk)
        if not obj:
            return self.not_found(request)

        if not self.has_delete_permission(obj, request):
            return self.no_delete_permission(request)

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def dispatch(self, request, *args, **kwargs):
        url_params = {}
        for param in self.url_params:
            if param in kwargs:
                url_params[param] = kwargs.pop(param)
        request.url_params = url_params
        return super().dispatch(request, *args, **kwargs)

    def create_default_params(self, request):
        return {}

    def additional_context_params(self, request):
        return {}

    def get_context(self, request):
        context = {'request': request}
        context.update(self.additional_context_params(request))
        return context

    def not_found(self, request):
        return ErrorResponse(errors.THE_REQUESTED_OBJECT_NOT_FOUND)

    def no_delete_permission(self, request):
        return ErrorResponse(errors.YOU_CANNOT_DELETE_THIS_OBJECT_AT_THIS_TIME)

    def no_update_permission(self, request):
        return ErrorResponse(errors.YOU_CANNOT_UPDATE_THIS_OBJECT_AT_THIS_TIME)

    def no_create_permission(self, request):
        return ErrorResponse(errors.YOU_CANNOT_CREATE_OBJECT_AT_THIS_TIME)

    def data_not_valid(self, request, data_errors):
        return ErrorResponse(errors.USER_INPUT_IS_NOT_VALID,
                             errors=data_errors)


class PaginatedViewSet(BaseViewSet):
    page_size = 20

    def get_pagination_class(self, objects, request):
        return PageNumberPagination(objects, request,
                                    page_size=self.page_size)

    def list(self, request):
        objects = self.get_queryset(request).all()
        paginated = self.get_pagination_class(objects, request)

        return Response(
            data=self.serializer_class(
                paginated.get_result(),
                many=True,
                context=self.get_context(request)
            ).data, headers=paginated.get_pagination_headers())
