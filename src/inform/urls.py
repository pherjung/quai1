from django.urls import path
from . import views
from . import legacy_views


urlpatterns = [
    path('exchanges', views.exchanges, name='exchanges'),
    path('exchanges/validate/', views.validate),
    path('legacy_exchanges/', legacy_views.exchanges, name='legacy_exchanges'),
    path('legacy_exchanges/delete/', legacy_views.delete),
    path('legacy_wishes/', legacy_views.wishes, name='legacy_wishes'),
    path('legacy_wishes/delete/', legacy_views.delete_wish),
    path('legacy_wishes/confirm/', legacy_views.validate_leave),
    path('legacy_wishes/confirm_shift/', legacy_views.validate_shift),
]
