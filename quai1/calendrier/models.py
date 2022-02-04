from django.db import models


class Shift(models.Model):
    shift_id = models.CharField(
                max_length=50,
                unique=True
                )
    shift_name = models.CharField(max_length=100)
    date = models.DateField()
    start_hour = models.TimeField(None)
    end_hour = models.TimeField(None)
