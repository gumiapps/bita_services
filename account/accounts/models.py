from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .manager import CustomUserManager


class User(AbstractUser):
    username = models.CharField(max_length=125)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(9|7)\d{8}$",
                message="Phone number must be entered in the format: '912345678 / 712345678'. Up to 9 digits allowed.",
            )
        ],
    )
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    def __str__(self):
        return self.email
