from django.contrib import admin

from .models import CustomUser, Depot


admin.site.register(CustomUser)
admin.site.register(Depot)
