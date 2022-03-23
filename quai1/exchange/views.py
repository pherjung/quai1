from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from datetime import datetime
from django.db.models import Q

from .forms import LeaveForms, AskLeaveForms
from calendrier.models import Shift
from .models import Give_leave, Ask_leave, Request_shift


def save_leave(request):
    if request.method == 'POST':
        form = LeaveForms(request.POST)

        try:
            if form.is_valid():
                cleaned_date = form.cleaned_data['date']
                form_date = datetime.strptime(cleaned_date, "%A %d %B %Y")
                Ask_leave.objects.filter(
                    giver_shift__owner__username=request.user,
                    giver_shift__date=form_date,
                ).update(gift=True)
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
            if form.cleaned_data['ask_rest'] == 'ask_rest':
                # Check if there is already asked leave
                wishes = Ask_leave.objects.filter(
                    user_shift__owner__username=request.user,
                    user_shift__date=form_date,
                )
                if not len(wishes):
                    # Recover all given leaves
                    leaves = Give_leave.objects.filter(
                        shift_id__date=form_date
                    ).exclude(
                        shift_id__owner_id__username=request.user
                    ).values_list('shift_id')
                    # Recover column ID of all leaves not owned by requester
                    give = Shift.objects.filter(
                        date=form_date,
                        start_hour=None,
                        shift_name__iregex=r'(C|R)T*'
                    ).exclude(owner=request.user)
                    # Save shifts
                    it = 0
                    gift = False
                    while it < len(give):
                        for i in range(len(leaves)):
                            gift = True if give[it].id in leaves[i] else False

                        save_asked = Ask_leave.objects.create(
                            user_shift=ask,
                            giver_shift=give[it],
                            note=user_note,
                            gift=gift
                        )
                        save_asked.save()
                        it += 1
                else:
                    print('There is already an asked leave')

            if form.cleaned_data['ask_rest'] == 'horary':
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
                    # Search between asked time
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
                ).exclude(owner__username=request.user)

                ti = 0
                while ti < len(shifts):
                    save_modify = Request_shift.objects.create(
                        user_shift=ask,
                        giver_shift=shifts[ti],
                        note=user_note,
                    )
                    save_modify.save()
                    ti += 1

    return HttpResponseRedirect(reverse('calendar'))
