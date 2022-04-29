from django.http import HttpResponseRedirect
from django.urls import reverse
from login.models import CustomUser
from calendarManager import main


def save_calendar(request):
    users = CustomUser.objects.all()
    user = users.last()
    main.write_data(user)
    for person in users:
        main.apply(person)

    return HttpResponseRedirect(reverse('calendar'))
