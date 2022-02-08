from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    pass
    url = models.URLField(max_length=150)
    depot = models.CharField(max_length=50)
    phoneNbRegex = RegexValidator(regex=r"^\+?1?[\s|\d]{8,25}$")
    phone_nb = models.CharField(validators=[phoneNbRegex],
                                max_length=16,
                                unique=True)

    def __str__(self):
        return self.username
