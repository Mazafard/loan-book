import binascii
import os

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from common.models import BaseModel


class AuthToken(BaseModel):
    value = models.CharField(db_index=True, max_length=255)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.PositiveIntegerField()
    user = GenericForeignKey()

    def save(self, *args, **kwargs):
        if not self.value:
            self.value = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    @classmethod
    def revoke(cls, payload):
        return cls.objects.filter(value=payload['token']).delete()

    @classmethod
    def get_new_auth_token(cls, user):
        jwt = cls(user=user)
        jwt.save()
        payload = jwt_payload_handler(user)
        payload['token'] = jwt.value
        payload['model'] = '{}.{}'.format(user._meta.app_label, user._meta.model_name)
        token = jwt_encode_handler(payload)
        return token


from rest_framework_jwt.serializers import jwt_payload_handler, \
    jwt_encode_handler
