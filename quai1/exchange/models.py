from django.db import models
from calendrier.models import Shift
from login.models import CustomUser


class Give_leave(models.Model):
    shift = models.OneToOneField(Shift,
                                 on_delete=models.DO_NOTHING)
    given = models.BooleanField(default=False)
    who = models.ForeignKey(CustomUser,
                            null=True,
                            on_delete=models.DO_NOTHING)


class Ask_leave(models.Model):
    user_shift = models.ForeignKey(Shift,
                                   related_name='asker',
                                   on_delete=models.DO_NOTHING)
    giver_shift = models.ForeignKey(Shift,
                                    related_name='giver',
                                    on_delete=models.DO_NOTHING)
    note = models.TextField(null=True)
    accepted = models.BooleanField(null=True)
    negotiate = models.BooleanField(default=False)
    gift = models.BooleanField()
    given_leave = models.ForeignKey(Shift,
                                    null=True,
                                    on_delete=models.DO_NOTHING)
