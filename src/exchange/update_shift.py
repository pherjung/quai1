from datetime import datetime

from calendrier.models import Shift
from .models import Give_leave, Request_leave, Request_shift
from .rest_time import start_end_hour


def search_leaves(user, log_id):
    """
    Search all existing wishes for a leave
    user->CustomUser
    log_id->exchange.models.Request_leave_log
    """
    # Recover all given leaves
    gifted_leaves = Give_leave.objects.filter(
        shift__date=log_id.date,
        shift__owner__depot__in=[x.id for x in user.depot.all()],
    ).exclude(shift__owner=user).values_list('shift_id').distinct()
    # Recover ID of all leaves not owned by requester
    available_leaves = Shift.objects.filter(
        date=log_id.date,
        start_hour=None,
        shift_name__iregex=r'(C|R)T*',
        owner__depot__in=[x.id for x in user.depot.all()]
    ).exclude(owner=user).distinct()
    return gifted_leaves, list(available_leaves)


def write_legal_leaves(user, log_id, user_shift):
    """
    Write legal leaves
    user->CustomUser
    log_id->exchange.models.Request_leave_log
    user_shift->calendrier.models.Shift
    """
    gifts, available_leaves = search_leaves(user, log_id)
    # Exclude unchangeable leaves
    legal_leaves = exclude_illegal(user_shift, available_leaves)
    # Save shifts
    give_it = 0
    gift = False  # Useful in case len(give) is 0
    while give_it < len(legal_leaves):
        for index in enumerate(gifts):
            gift = bool(available_leaves[give_it].id in gifts[index[0]])

        Request_leave.objects.get_or_create(
            user_shift=user_shifts,
            giver_shift=available_leaves[give_it],
            note=log_id.note,
            validated=gift,
            request=log_id,
        )
        give_it += 1


def search_shifts(user, form, form_date, switch):
    """
    Search
    user->CustomUser object
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

    query = {'date': form_date,
             'depot__in': [x.id for x in user.depot.all()],
             }
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


def exclude_illegal(user_shift, shifts):
    """
    Keep only legal shifts
    user_shift->Shift object
    shifts->QuerySet
    return only legal shifts
    """
    users_shifts = list(shifts)
    remove = set()
    for tour in users_shifts:
        # Check if my shift is legal for tour.owner
        time_range = start_end_hour(user_shift.date, tour.owner.username)
        if user_shift.start_hour and user_shift.start_hour < time_range['start_hour']:
            remove.add(tour)
        if user_shift.end_hour and user_shift.end_hour > time_range['end_hour']:
            remove.add(tour)

    [users_shifts.remove(illegal) for illegal in remove]
    return users_shifts


def write_legal_shifts(user_shift, shifts, note, log):
    """
    Write legal shifts
    user_shift->Shift object
    shifts->QuerySet
    note->str
    log->Request_shift_log object
    """
    users_shifts = exclude_illegal(user_shift, shifts)
    shift_it = 0
    while shift_it < len(users_shifts):
        Request_shift.objects.create(
            user_shift=user_shift,
            giver_shift=shifts[shift_it],
            note=note,
            request=log,
        )
        shift_it += 1
