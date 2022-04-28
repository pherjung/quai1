from django.urls import reverse_lazy
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from calendarManager import main
from .forms import CustomUserCreationForm
from .models import CustomUser


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('update')
    template_name = 'registration/signup.html'


def save_calendar(request):
    users = CustomUser.objects.all()
    user = users.last()
    main.write_data(user)
    for person in users:
        main.apply(person)

    return HttpResponseRedirect(reverse('calendar'))
