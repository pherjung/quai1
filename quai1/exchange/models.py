from django.db import models
from calendrier.models import Shift


class Give_rest(models.Model):
    shift = models.ForeignKey(Shift,
                              on_delete=models.DO_NOTHING)


class Ask_rest(models.Model):
    user_shift = models.ForeignKey(Shift,
                                   related_name='asker',
                                   on_delete=models.DO_NOTHING)
    giver_shift = models.ForeignKey(Shift,
                                    related_name='giver',
                                    on_delete=models.DO_NOTHING)
