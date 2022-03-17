from django.urls import path
from . import views


urlpatterns = [
    path('exchanges/', views.exchanges, name='exchanges'),
    path('exchanges/validate/', views.validate),
    path('exchanges/delete/', views.delete),
    path('wishes/', views.wishes, name='wishes'),
]
