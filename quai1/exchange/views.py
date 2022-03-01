from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime

from .forms import RestForms
from calendrier.models import Shift
from .models import Give_rest


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
