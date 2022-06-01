from datetime import datetime
from django.db.models import Q

from calendrier.models import Shift
from .models import Give_leave, Request_leave, Request_shift
from .rest_time import start_end_hour


def search_leaves(user, log_id, user_shift):
    """
    Search all existing wishes for a leave
    user->str
    log_id->exchange.models.Request_leave_log
    user_shift->calendrier.models.Shift
    """
    # Recover all given leaves
    leaves = Give_leave.objects.filter(
        shift_id__date=log_id.date
    ).exclude(
        shift_id__owner_id__username=user
    ).values_list('shift_id')
    # Recover ID of all leaves not owned by requester
    give = Shift.objects.filter(
        date=log_id.date,
        start_hour=None,
        shift_name__iregex=r'(C|R)T*'
    ).exclude(owner__username=user)
    # Exclude unchangeable leaves
    legal_leaves = list(give)
    illegal_leaves = set()
    for i in legal_leaves:
        time_range = start_end_hour(log_id.date, i.owner.username)
        print('debug test', time_range, i.owner.username)
        if user_shift.start_hour < time_range['start_hour']:
            print('illegal start, to-do')
            illegal_leaves.add(i)
        if user_shift.end_hour > time_range['end_hour']:
            print('illegal end, to-do')
            illegal_leaves.add(i)

    [legal_leaves.remove(illegal) for illegal in illegal_leaves]
    # Save shifts
    give_it = 0
    gift = False  # Useful in case len(give) is 0
    while give_it < len(legal_leaves):
        for index in enumerate(leaves):
            gift = bool(give[give_it].id in leaves[index[0]])

        Request_leave.objects.get_or_create(
            user_shift=user_shift,
            giver_shift=legal_leaves[give_it],
            note=log_id.note,
            validated=gift,
            request=log_id,
        )
        give_it += 1


def search_shifts(form, form_date, switch):
    """
    Search
    form->
    form_date->
    switch->Boolean
    """
    if switch:
        start_hour1 = form.cleaned_data['start_hour_1']
        start_hour2 = form.cleaned_data['start_hour_2']
        end_hour1 = form.cleaned_data['end_hour_1']
        end_hour2 = form.cleaned_data['end_hour_2']
        tolerance_end = form.cleaned_data['tolerance_end']
        tolerance_start = form.cleaned_data['tolerance_start']
    else:
        start_hour1 = form.start_hour1
        start_hour2 = form.start_hour2
        end_hour1 = form.end_hour1
        end_hour2 = form.end_hour2
        tolerance_end = form.tolerance_end
        tolerance_start = form.tolerance_start

    query = {'date': form_date}
    condition = 0
    condition += bool(start_hour1)
    condition += bool(start_hour2)
    condition += 3 if end_hour1 else 0
    condition += 3 if end_hour2 else 0
    match condition:
        # Search starting from start_minus
        case 1:
            start = start_hour1 if start_hour1 else start_hour2
            minus = datetime.combine(form_date, start) - tolerance_start
            query['start_hour__gt'] = minus
        # Search between start_minus and start_plus
        case 2:
            minus = datetime.combine(form_date, start_hour1) - tolerance_start
            plus = datetime.combine(form_date, start_hour2) + tolerance_start
            query['start_hour__range'] = [minus, plus]
        # Search starting from end_minus
        # Search between requested time
        case 3:
            end = end_hour1 if end_hour1 else end_hour2
            plus = datetime.combine(form_date, end) + tolerance_end
            query['end_hour__lt'] = plus
        # Search between end_minus and end_plus
        case 6:
            minus = datetime.combine(form_date, end_hour1) - tolerance_end
            plus = datetime.combine(form_date, end_hour2) + tolerance_end
            query['end_hour__range'] = [minus, plus]
        case 4:
            start = start_hour1 if start_hour1 else start_hour2
            minus = datetime.combine(form_date, start) - tolerance_start
            end = end_hour1 if end_hour1 else end_hour2
            plus = datetime.combine(form_date, end) + tolerance_end
            query['start_hour__gt'] = minus
            query['end_hour__lt'] = plus
        case _:
            # To-do
            print('catch false case')
    return query


def keep_legal_shifts(user_shift, shifts, date, note, log):
    """
    Keep only legal shifts
    user_shift->Shift object
    shifts->QuerySet
    date->datetime object
    note->str
    log->Request_shift_log object
    """
    users_shifts = list(shifts)
    remove = set()
    for tour in users_shifts:
        time_range = start_end_hour(date, tour.owner.username)
        if user_shift.start_hour < time_range['start_hour']:
            print('illegal, to-do', date, tour.owner.username)
            remove.add(tour)
        if user_shift.end_hour > time_range['end_hour']:
            print('illegal, to-do', date, tour.owner.username)
            remove.add(tour)

    [users_shifts.remove(illegal) for illegal in remove]
    shift_it = 0
    while shift_it < len(users_shifts):
        Request_shift.objects.create(
            user_shift=user_shift,
            giver_shift=shifts[shift_it],
            note=note,
            request=log,
        )
        shift_it += 1
