from django.contrib import admin
from .models import Give_leave, Request_leave, Request_shift, Request_log


admin.site.register(Give_leave)
admin.site.register(Request_leave)
admin.site.register(Request_shift)
admin.site.register(Request_log)
