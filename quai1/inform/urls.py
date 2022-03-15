from django.urls import path
from . import views


urlpatterns = [
    path('exchanges/', views.exchanges, name='exchanges'),
    path('wishes/', views.wishes, name='wishes'),
]
