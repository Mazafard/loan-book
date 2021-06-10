import uuid

from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import NotFound


class BaseModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_by_pk(cls, pk, raise_exception=False) -> 'BaseModel':
        obj = cls.objects.filter(pk=pk).first()
        if raise_exception and not obj:
            raise NotFound('The requested entity is not found')
        return obj

    @classmethod
    def get_all(cls):
        return cls.objects.all()

    @classmethod
    def first_or_create(cls, **kwargs):
        obj = cls.objects.filter(**kwargs).first()
        if not obj:
            obj = cls(**kwargs)
            obj.save()
        return obj

    def load(self, **kwargs):
        for key, value in kwargs.items():
            assert key not in self._meta.fields, \
                """The requested field %s not exists""" % str(key)
            setattr(self, key, value)
        return self


class BaseUserModel(AbstractBaseUser):
    user_uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    SYSTEM_TEXT_EMAIL_TYPE = None
    id = models.BigAutoField(
        primary_key=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    email = models.EmailField(
        unique=True,
    )
    email_verification_code = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=True
    )
    is_email_verified = models.BooleanField(
        default=False
    )
    email_verified_at = models.DateTimeField(blank=True, null=True)
    first_name = models.CharField(
        max_length=255
    )
    last_name = models.CharField(
        max_length=255
    )
    USERNAME_FIELD = 'email'

    class Meta:
        abstract = True

    @property
    def username(self):
        return self.email

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return False

    def update_last_login(self):
        self.last_login = timezone.now()
        self.save()

    def get_new_auth_token(self) -> str:
        self.update_last_login()
        AuthToken = apps.get_model('service.AuthToken')
        return AuthToken.get_new_auth_token(self)

    @classmethod
    def get_by_email(cls, email) -> 'BaseUserModel':
        return cls.objects.filter(email=email).first()
