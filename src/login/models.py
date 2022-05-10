from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class CustomUser(AbstractUser):
    pass
    DEPOTS = (
        ('GENEVE', 'Genève'),
        ('LAUSANNE', 'Lausanne'),
        ('VALLORBE', 'Vallorbe'),
        ('BIEL/BIENNE', 'Biel/Bienne'),
        ('CHAUX-DE-FONDS', 'Chaux-de-Fonds'),
        ('DELEMONT', 'Délémont'),
        ('FRIBOURG', 'Fribourg'),
        ('NEUCHATEL', 'Neuchâtel'),
        ('PAYERNE', 'Payerne'),
        ('FRIBOURG', 'Fribourg'),
        ('ST-MAURICE', 'St-Maurice'),
        ('VEVEY', 'Vevey')

    )
    url = models.URLField('URL du calendrier SOPREweb',
                          max_length=150)
    depot = models.CharField('Dépôt',
                             max_length=14,
                             choices=DEPOTS)
    phoneNbRegex = RegexValidator(regex=r"^\+?1?[\s|\d]{8,25}$")
    phone_nb = models.CharField('Phone number',
                                validators=[phoneNbRegex],
                                max_length=16,
                                unique=True)

    def __str__(self):
        return self.username
