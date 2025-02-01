from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .manager import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, blank=True)  # Overriden to make it unique
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(9|7)\d{8}$",
                message="Phone number must be entered in the format: '912345678 / 712345678'. Up to 9 digits allowed.",
            )
        ],
        unique=True,
        blank=True,
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name"]

    def __str__(self):
        return self.email


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(9|7)\d{8}$",
                message="Phone number must be entered in the format: '912345678 / 712345678'. Up to 9 digits allowed.",
            )
        ],
    )
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^(9|7)\d{8}$",
                message="Phone number must be entered in the format: '912345678 / 712345678'. Up to 9 digits allowed.",
            )
        ],
    )
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
