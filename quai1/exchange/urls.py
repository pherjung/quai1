from django.urls import path
from . import views


urlpatterns = [
    path('validate/', views.save_leave, name='form'),
    path('validate_shift/', views.request_leave, name='request_leave'),
]
