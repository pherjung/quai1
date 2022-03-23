from django.contrib import admin
from .models import Give_leave, Ask_leave, Request_shift


admin.site.register(Give_leave)
admin.site.register(Ask_leave)
admin.site.register(Request_shift)
