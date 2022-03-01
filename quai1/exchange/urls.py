from django.urls import path
from . import views


urlpatterns = [
    path('calendar/validate/', views.save_rest, name='form')
]
