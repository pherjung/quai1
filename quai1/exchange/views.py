from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime

from .forms import LeaveForms, AskLeaveForms
from calendrier.models import Shift
from .models import Give_leave, Ask_leave


def save_leave(request):
    if request.method == 'POST':
        form = LeaveForms(request.POST)

        try:
            if form.is_valid():
                cleaned_date = form.cleaned_data['date']
                form_date = datetime.strptime(cleaned_date, "%A %d %B %Y")
                give = Shift.objects.get(date=form_date, owner=request.user)
                save_gived = Give_leave.objects.create(shift=give)
                save_gived.save()
        except IntegrityError:
            print('Congé déjà posé')
        return HttpResponseRedirect(reverse('calendar'))


def ask_leave(request):
    if request.method == 'POST':
        form = AskLeaveForms(request.POST)

        if form.is_valid():
            asked_date = form.cleaned_data['date']
            user_note = form.cleaned_data['note']
            form_date = datetime.strptime(asked_date, "%A %d %B %Y")
            ask = Shift.objects.get(date=form_date, owner=request.user)
            # Recover all given leaves
            leaves = Give_leave.objects.filter(
                shift_id__date=form_date
            ).exclude(
                shift_id__owner_id__username=request.user
            ).values_list('shift_id')
            # Recover column ID of all leaves not owned by requester
            givers = Shift.objects.filter(
                date=form_date,
                start_hour=None,
                shift_name__iregex=r'(C|R)T*'
            ).exclude(owner=request.user)
            # Save shifts
            item = 0
            gifted = False
            while item < len(givers):
                for i in range(len(leaves)):
                    gifted = True if givers[item].id in leaves[i] else False

                save_asked = Ask_leave.objects.create(user_shift=ask,
                                                      giver_shift=givers[item],
                                                      note=user_note,
                                                      gift=gifted)
                save_asked.save()
                item += 1

    return HttpResponseRedirect(reverse('calendar'))
