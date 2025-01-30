from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .manager import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)  # Overriden to make it unique
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(9|7)\d{8}$",
                message="Phone number must be entered in the format: '912345678 / 712345678'. Up to 9 digits allowed.",
            )
        ],
        unique=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "email"]

    def __str__(self):
        return self.email
