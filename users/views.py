from django.utils.decorators import method_decorator
from rest_framework import status

from common.response import Response
from common.views import BaseAPIView
from users import serializers
from users.swagger import user_login_post, user_register_post


class RegisterView(BaseAPIView):
    @method_decorator(name='post', decorator=user_register_post)
    def post(self, request):
        serializer = serializers.RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )


class LoginViewSet(BaseAPIView):

    @method_decorator(name='post', decorator=user_login_post)
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            data={
                'jwt_token': serializer.instance.get_new_auth_token(),
            }
        )
