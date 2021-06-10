from django.db.transaction import atomic
from rest_framework import serializers

from common.serializers import BaseSerializer, BaseModelSerializer
from users.models import Customer


class RegisterSerializer(BaseModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'first_name',
            'last_name',
            'email',
            'password',
        )

    @atomic
    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = super().create(validated_data)  # type: Customer
        instance.set_password(password)
        instance.save()
        # instance.send_verification_email()
        return instance


class LoginResponseSerializer(BaseSerializer):
    jwt_token = serializers.CharField()


class LoginSerializer(BaseSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attr):
        self.instance = Customer.get_by_email(
            email=attr['email']
        )
        if not self.instance:
            raise serializers.ValidationError({'email': 'Invalid Credential.'})
        if not self.instance.check_password(attr['password']):
            raise serializers.ValidationError({'password': 'Invalid Credential.'})
        return attr


class CustomerSerializer(BaseModelSerializer):
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(min_length=6)

    class Meta:
        model = Customer
        fields = (
            'id',
            'first_name',
            'last_name',
            'is_owner',
            'email',
            'password',
        )
