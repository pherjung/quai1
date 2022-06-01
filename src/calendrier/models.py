from django.db import models
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from login.models import CustomUser, Depot


class Shift(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    shift_name = models.CharField(max_length=100)
    depot = models.ForeignKey(Depot,
                              null=True,
                              on_delete=models.DO_NOTHING)
    date = models.DateField()
    start_hour = models.DateTimeField(null=True)
    end_hour = models.DateTimeField(null=True)
    owner = models.ForeignKey(CustomUser,
                              on_delete=models.DO_NOTHING)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['date', 'owner'],
                                               name='unique_shift')]
