import random
import string

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

# Create your models here.
from backend import settings
from common.models import BaseUserModel


class Customer(BaseUserModel):
    reset_password_token = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    tokens = GenericRelation(
        'service.AuthToken',
        related_name='customer'
    )

    @classmethod
    def get_by_reset_password_token(cls, reset_password_token) -> 'Customer':
        return cls.objects.filter(reset_password_token=reset_password_token).first()

    def generate_reset_password_token(self):
        self.reset_password_token = ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in
            range(settings.EMAIL_VERIFICATION_CODE_SIZE))
        self.save()

    @property
    def is_customer(self):
        return True

    def get_loans(self):
        from book.models import BookLoanHistory
        return BookLoanHistory.objects.filter(
            customer=self)
