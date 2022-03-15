from django.db import models
from calendrier.models import Shift


class Give_leave(models.Model):
    shift = models.OneToOneField(Shift,
                                 on_delete=models.DO_NOTHING)
    given = models.BooleanField(default=False)


class Ask_leave(models.Model):
    user_shift = models.ForeignKey(Shift,
                                   related_name='asker',
                                   on_delete=models.DO_NOTHING)
    giver_shift = models.ForeignKey(Shift,
                                    related_name='giver',
                                    on_delete=models.DO_NOTHING)
    note = models.TextField(null=True)
    accepted = models.BooleanField(null=True)
    gift = models.BooleanField()
