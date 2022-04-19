from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Q

from calendrier.models import Shift
from .forms import LeaveForms, RequestLeaveForms
from .models import Give_leave, Request_leave, Request_shift, Request_log
from .update_shift import search_wishes, search_shifts


def save_leave(request):
    if request.method == 'POST':
        form = LeaveForms(request.POST)

        try:
            if form.is_valid():
                cleaned_date = form.cleaned_data['date']
                form_date = datetime.strptime(cleaned_date, "%A %d %B %Y")
                Request_leave.objects.filter(
                    giver_shift__owner__username=request.user,
                    giver_shift__date=form_date,
                ).update(gift=True)
                give = Shift.objects.get(date=form_date, owner=request.user)
                save_gived = Give_leave.objects.create(shift=give)
                save_gived.save()
        except IntegrityError:
            print('Congé déjà posé')
        return HttpResponseRedirect(reverse('calendar'))


def request_leave(request):
    if request.method == 'POST':
        form = RequestLeaveForms(request.POST)
        if form.is_valid():
            requested_date = form.cleaned_data['date']
            form_date = datetime.strptime(requested_date, "%A %d %B %Y")
            request_data = Shift.objects.get(date=form_date,
                                             owner=request.user)
            user_note = form.cleaned_data['note']
            if form.cleaned_data['request_leave'] == 'request_leave':
                search_wishes(request.user,
                              form_date,
                              request_data,
                              user_note)
            elif form.cleaned_data['request_leave'] == 'schedule':
                query = search_shifts(form,
                                      form_date,
                                      True)
                # Shift starting from range start_hour_1 +/- tolerance
                shifts = Shift.objects.filter(
                    Q(**query)
                    | Q(date=form_date,
                        shift_name__iregex=(r'^200'))
                ).exclude(owner=request.user)
                log = Request_log.objects.create(
                    user=request.user,
                    date=form_date,
                    start_hour1=form.cleaned_data['start_hour_1'],
                    start_hour2=form.cleaned_data['start_hour_2'],
                    tolerance_start=form.cleaned_data['tolerance_start'],
                    end_hour1=form.cleaned_data['end_hour_1'],
                    end_hour2=form.cleaned_data['end_hour_2'],
                    tolerance_end=form.cleaned_data['tolerance_end'],
                    note=user_note
                )
                log.save()

                shift_it = 0
                while shift_it < len(shifts):
                    Request_shift.objects.create(
                        user_shift=request_data,
                        giver_shift=shifts[shift_it],
                        note=user_note,
                        request=log,
                    ).save()
                    shift_it += 1

    return HttpResponseRedirect(reverse('calendar'))
