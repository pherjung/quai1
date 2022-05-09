from django.db import models
from login.models import CustomUser
from bulk_update_or_create import BulkUpdateOrCreateQuerySet


class Shift(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    shift_id = models.CharField(
                max_length=50,
                unique=True
                )
    shift_name = models.CharField(max_length=100)
    date = models.DateField()
    start_hour = models.TimeField(null=True)
    end_hour = models.TimeField(null=True)
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.DO_NOTHING)
