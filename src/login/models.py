from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class Depot(models.Model):
    name = models.CharField('Dépôt',
                            max_length=20)
    region = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    pass
    url = models.URLField('URL du calendrier SOPREweb',
                          max_length=150)
    depot = models.ManyToManyField(Depot)
    phoneNbRegex = RegexValidator(regex=r"^\+?1?[\s|\d]{8,25}$")
    phone_nb = models.CharField('Phone number',
                                validators=[phoneNbRegex],
                                max_length=16,
                                unique=True)

    def __str__(self):
        return self.username
