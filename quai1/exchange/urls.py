from django.urls import path
from . import views


urlpatterns = [
    path('validate/', views.save_leave, name='form'),
    path('validate_shift/', views.ask_leave, name='ask_rest'),
]
