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


class Request_log(models.Model):
    user = models.ForeignKey(CustomUser,
                             on_delete=models.DO_NOTHING)
    date = models.DateField()
    start_hour1 = models.TimeField(null=True)
    start_hour2 = models.TimeField(null=True)
    tolerance_start = models.DurationField(null=True)
    end_hour1 = models.TimeField(null=True)
    end_hour2 = models.TimeField(null=True)
    tolerance_end = models.DurationField(null=True)
    note = models.TextField(null=True)
    active = models.BooleanField(default=True)


class Request_leave(models.Model):
    user_shift = models.ForeignKey(Shift,
                                   related_name='requester_leave',
                                   on_delete=models.DO_NOTHING)
    giver_shift = models.ForeignKey(Shift,
                                    related_name='giver_leave',
                                    on_delete=models.DO_NOTHING)
    note = models.TextField(null=True)
    accepted = models.BooleanField(null=True)
    validated = models.BooleanField()
    given_shift = models.ForeignKey(Shift,
                                    null=True,
                                    on_delete=models.DO_NOTHING)


class Request_shift(models.Model):
    user_shift = models.ForeignKey(Shift,
                                   related_name='requester_shift',
                                   on_delete=models.DO_NOTHING)
    giver_shift = models.ForeignKey(Shift,
                                    related_name='request_shift',
                                    on_delete=models.DO_NOTHING)
    note = models.TextField(null=True)
    accepted = models.BooleanField(null=True)
    confirmed = models.BooleanField(default=False)
    request = models.ForeignKey(Request_log,
                                on_delete=models.DO_NOTHING)
