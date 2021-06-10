from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from users import serializers

# ==================================
#   API Responses
# ==================================
RESPONSE_USER_REGISTER_POST = {
    status.HTTP_204_NO_CONTENT: '',
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
}

RESPONSE_USER_LOGIN_POST = {
    status.HTTP_200_OK: serializers.LoginResponseSerializer(),
    status.HTTP_401_UNAUTHORIZED: 'Authentication credentials were not provided.',
}

# ==================================
#     Tenant Swagger Decorators
# ==================================
user_login_post = swagger_auto_schema(
    operation_description='login user ',
    responses=RESPONSE_USER_LOGIN_POST,
    request_body=serializers.LoginSerializer(),

)
user_register_post = swagger_auto_schema(
    operation_description='Rregister User',
    responses=RESPONSE_USER_REGISTER_POST,
    request_body=serializers.RegisterSerializer(),

)
