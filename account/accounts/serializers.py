import json
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from environs import Env

# Initialize environs
env = Env()
env.read_env()  # read .env file, if it exists

User = get_user_model()

email_url = env.str("NOTIFICATION_API_URL") + "/api/send-single-email/"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "username", "password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request", None)
        if request and request.method != "POST":
            fields.pop("password", None)
        return fields

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def save(self):
        request = self.context.get("request")
        user = User.objects.get(email=self.validated_data["email"])
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f"{request.scheme}://{request.get_host()}/accounts/password-reset-confirm/{uid}/{token}/"
        email_message = "Click the link below to reset your password:\n\n" + reset_url
        email_subject = "Password Reset"
        recipients = user.email
        payload = json.dumps(
            {
                "subject": email_subject,
                "message": email_message,
                "recipients": recipients,
            }
        )
        headers = {
            "Authorization": f"Api-Key {env.str('NOTIFICATION_API_KEY')}",
            "Content-Type": "application/json",
        }
        response = requests.request("POST", email_url, headers=headers, data=payload)
        print(response.text)


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def save(self, user):
        user.set_password(self.validated_data["password"])
        user.save()
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is not correct.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError("New passwords do not match.")
        return attrs

    def save(self, user):
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["email"] = user.email
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data.update(
            {
                "user": {
                    "id": self.user.id,
                    "email": self.user.email,
                    "username": self.user.username,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "phone": self.user.phone,
                }
            }
        )
        return data
