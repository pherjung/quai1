from django.urls import path
from . import views
from . import legacy_views


urlpatterns = [
    path('gifts/', views.gifts),
    path('exchanges', views.exchanges, name='exchanges'),
    path('exchanges/validate/', views.validate),
    path('to_accept_leave', views.to_accept_leave),
    path('confirm_leave/', views.confirm_leave),
    path('to_accept_shift', views.to_accept_shift),
    path('confirm_shift/', views.confirm_shift),
    path('wishes/', views.wishes),
    path('legacy_exchanges/', legacy_views.exchanges, name='legacy_exchanges'),
    path('legacy_exchanges/delete/', legacy_views.delete),
    path('legacy_wishes/', legacy_views.wishes, name='legacy_wishes'),
    path('legacy_wishes/delete/', legacy_views.delete_wish),
    path('legacy_wishes/confirm/', legacy_views.validate_leave),
    path('legacy_wishes/confirm_shift/', legacy_views.validate_shift),
]
