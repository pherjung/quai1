from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

from .forms import RestForms, AskRestForms
from calendrier.models import Shift
from .models import Give_rest, Ask_rest


def save_rest(request):
    if request.method == 'POST':
        form = RestForms(request.POST)

        if form.is_valid():
            cleaned_date = form.cleaned_data['date']
            form_date = datetime.strptime(cleaned_date, "%A %d %B %Y")
            give = Shift.objects.get(date=form_date, owner=request.user)
            save_gived = Give_rest.objects.create(shift=give)
            save_gived.save()

    return HttpResponseRedirect(reverse('calendar'))


def ask_rest(request):
    if request.method == 'POST':
        form = AskRestForms(request.POST)

        if form.is_valid():
            asked_date = form.cleaned_data['date']
            form_date = datetime.strptime(asked_date, "%A %d %B %Y")
            ask = Shift.objects.get(date=form_date, owner=request.user)
            givers = Shift.objects.filter(
                date=form_date,
                start_hour=None,
                shift_name__iregex=r'(C|R)T*'
            ).exclude(owner=request.user)
            for rest in givers:
                save_asked = Ask_rest.objects.create(user_shift=ask,
                                                     giver_shift=rest)
                save_asked.save()

    return HttpResponseRedirect(reverse('calendar'))
