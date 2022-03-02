from django.urls import path
from . import views


urlpatterns = [
    path('validate/', views.save_rest, name='form'),
    path('validate_shift/', views.ask_rest, name='ask_rest'),
]
