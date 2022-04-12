from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Q

from calendrier.models import Shift
from .forms import LeaveForms, RequestLeaveForms
from .models import Give_leave, Request_leave, Request_shift, Request_log


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
        user = request.user

        if form.is_valid():
            requested_date = form.cleaned_data['date']
            user_note = form.cleaned_data['note']
            form_date = datetime.strptime(requested_date, "%A %d %B %Y")
            request_data = Shift.objects.get(date=form_date, owner=user)
            if form.cleaned_data['request_leave'] == 'request_leave':
                # Check if there is already requested leave
                wishes = Request_leave.objects.filter(
                    user_shift__owner__username=user,
                    user_shift__date=form_date,
                )
                if not wishes:
                    # Recover all given leaves
                    leaves = Give_leave.objects.filter(
                        shift_id__date=form_date
                    ).exclude(
                        shift_id__owner_id__username=user
                    ).values_list('shift_id')
                    # Recover column ID of all leaves not owned by requester
                    give = Shift.objects.filter(
                        date=form_date,
                        start_hour=None,
                        shift_name__iregex=r'(C|R)T*'
                    ).exclude(owner=user)
                    # Save shifts
                    give_it = 0
                    gift = False  # Useful in case len(give) is 0
                    while give_it < len(give):
                        for index in enumerate(leaves):
                            gift = bool(give[give_it].id in leaves[index[0]])

                        save_requested = Request_leave.objects.create(
                            user_shift=request_data,
                            giver_shift=give[give_it],
                            note=user_note,
                            gift=gift
                        )
                        save_requested.save()
                        give_it += 1
                else:
                    print('There is already an requested leave')

            if form.cleaned_data['request_leave'] == 'schedule':
                condition = 0
                start_hour1 = form.cleaned_data['start_hour_1']
                condition += 1 if start_hour1 else 0
                start_hour2 = form.cleaned_data['start_hour_2']
                condition += 1 if start_hour2 else 0
                # End stuff
                end_hour1 = form.cleaned_data['end_hour_1']
                condition += 3 if end_hour1 else 0
                end_hour2 = form.cleaned_data['end_hour_2']
                condition += 3 if end_hour2 else 0
                tolerance_end = form.cleaned_data['tolerance_end']
                # default value should be set to tolerance_start
                tolerance_start = form.cleaned_data['tolerance_start']
                query = {'date': form_date}
                match condition:
                    # Search starting from start_minus
                    case 1:
                        start = start_hour1 if start_hour1 else start_hour2
                        start_minus = (datetime.combine(
                            form_date,
                            start) - tolerance_start).time()
                        query['start_hour__gt'] = start_minus
                    # Search between start_minus and start_plus
                    case 2:
                        start_minus = (datetime.combine(
                            form_date,
                            start_hour1) - tolerance_start).time()
                        start_plus = (datetime.combine(
                            form_date,
                            start_hour2) + tolerance_start).time()
                        query['start_hour__range'] = [start_minus, start_plus]
                    # Search starting from end_minus
                    # Search between requested time
                    case 3:
                        end = end_hour1 if end_hour1 else end_hour2
                        end_plus = (datetime.combine(
                            form_date,
                            end) + tolerance_end).time()
                        query['end_hour__lt'] = end_plus
                    # Search between end_minus and end_plus
                    case 6:
                        end_minus = (datetime.combine(
                            form_date,
                            end_hour1) - tolerance_end).time()
                        end_plus = (datetime.combine(
                            form_date,
                            end_hour2) + tolerance_end).time()
                        query['end_hour__range'] = [end_minus, end_plus]
                    case 4:
                        start = start_hour1 if start_hour1 else start_hour2
                        start_minus = (datetime.combine(
                            form_date,
                            start) - tolerance_start).time()
                        query['start_hour__gt'] = start_minus
                        end = end_hour1 if end_hour1 else end_hour2
                        end_plus = (datetime.combine(
                            form_date,
                            end) + tolerance_end).time()
                        query['end_hour__lt'] = end_plus
                    case _:
                        # To-do
                        print('catch false case')

                # Shift starting from range start_hour_1 +/- tolerance
                shifts = Shift.objects.filter(
                    Q(**query)
                    | Q(date=form_date,
                        shift_name__iregex=(r'^200'))
                ).exclude(owner=user)
                log = Request_log.objects.create(
                    user=request.user,
                    date=form_date,
                    start_hour1=start_hour1,
                    start_hour2=start_hour2,
                    tolerance_start=tolerance_start,
                    end_hour1=end_hour1,
                    end_hour2=end_hour2,
                    tolerance_end=tolerance_end,
                )
                log.save()

                shift_it = 0
                while shift_it < len(shifts):
                    save_modify = Request_shift.objects.create(
                        user_shift=request_data,
                        giver_shift=shifts[shift_it],
                        note=user_note,
                        request=log,
                    )
                    save_modify.save()
                    shift_it += 1

    return HttpResponseRedirect(reverse('calendar'))
