from django.db import models
from calendrier.models import Shift


class Give_rest(models.Model):
    shift = models.ForeignKey(Shift,
                              on_delete=models.DO_NOTHING)
