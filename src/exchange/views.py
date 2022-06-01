from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Q

from calendrier.models import Shift
from .forms import LeaveForms, RequestLeaveForms
from .models import Give_leave, Request_leave, Request_shift_log, Request_leave_log
from .update_shift import search_leaves, search_shifts, write_legal_shifts
from .rest_time import start_end_hour


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
                ).update(validated=True)
                give = Shift.objects.get(date=form_date, owner=request.user)
                Give_leave.objects.create(shift=give)
        except IntegrityError:
            print('Congé déjà posé')
        return HttpResponseRedirect(reverse('calendar'))


def request_leave(request):
    if request.method == 'POST':
        form = RequestLeaveForms(request.POST)
        if form.is_valid():
            requested_date = form.cleaned_data['date']
            form_date = datetime.strptime(requested_date, "%A %d %B %Y")
            hour_range = start_end_hour(form_date.date(), request.user)
            user_shift = Shift.objects.get(date=form_date,
                                           owner=request.user)
            note = form.cleaned_data['note']
            if form.cleaned_data['request_leave'] == 'request_leave':
                wishes, created = Request_leave_log.objects.update_or_create(
                    user=request.user, date=form_date,
                    defaults={'note': note,
                              'active': True},
                )
                if created:
                    search_leaves(request.user, wishes, user_shift)
            elif form.cleaned_data['request_leave'] == 'schedule':
                query = search_shifts(form, form_date, True)
                # Shift starting from range start_hour_1 +/- tolerance
                shifts = Shift.objects.filter(
                    Q(**query)
                    | Q(date=form_date,
                        shift_name__iregex=(r'^200'))
                ).exclude(Q(owner=request.user)
                          | Q(start_hour__lt=hour_range['start_hour'])
                          | Q(end_hour__gt=hour_range['end_hour'])
                          ).distinct()
                log = Request_shift_log.objects.create(
                    user=request.user,
                    date=form_date,
                    start_hour1=form.cleaned_data['start_hour_1'],
                    start_hour2=form.cleaned_data['start_hour_2'],
                    tolerance_start=form.cleaned_data['tolerance_start'],
                    end_hour1=form.cleaned_data['end_hour_1'],
                    end_hour2=form.cleaned_data['end_hour_2'],
                    tolerance_end=form.cleaned_data['tolerance_end'],
                    note=note
                )
                write_legal_shifts(user_shift, shifts, form_date, note, log)

    return HttpResponseRedirect(reverse('calendar'))
