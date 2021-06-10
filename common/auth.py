import jwt

from django.apps import apps
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


def jwt_decode_handler(token, verify_exp=api_settings.JWT_VERIFY_EXPIRATION):
    options = {
        'verify_exp': verify_exp,
    }

    return jwt.decode(
        token,
        api_settings.JWT_SECRET_KEY,
        api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
    )


class JWTTokenAuthentication(JSONWebTokenAuthentication):
    def authenticate(self, request):
        """
                Returns a two-tuple of `User` and token if a valid signature has been
                supplied using JWT-based authentication.  Otherwise returns `None`.
                """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = 'Signature has expired.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = 'Error decoding signature.'
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)
        request.user_payload = payload

        return user, jwt_value

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """

        username = payload['token'] if 'token' in payload else None
        model_full_name = payload['model'] if 'model' in payload else None

        if not username:
            msg = 'Invalid payload.'
            raise exceptions.AuthenticationFailed(msg)

        if not model_full_name:
            msg = 'Invalid payload.'
            raise exceptions.AuthenticationFailed(msg)

        UserModel = apps.get_model(model_full_name)
        try:
            user = UserModel.objects.filter(
                tokens__value=payload['token']
            ).get()
        except UserModel.DoesNotExist:
            msg = 'Invalid signature.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'User account is disabled.'
            raise exceptions.AuthenticationFailed(msg)

        return user
