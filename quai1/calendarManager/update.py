from datetime import datetime, timedelta
from django.db.models import Q
import re

from calendrier.models import Shift
from exchange.models import Request_shift_log, Request_shift, Request_leave_log


def shift_log_ids(user):
    """
    Fetch all logs from a user
    user->int
    return a QuerySet with dict
    """
    today = datetime.now().strftime("%Y-%m-%d")
    data = Request_shift_log.objects.filter(
        user__id=user,
        date__gt=today,
        active=True,
    ).values(
        'id',
        'date',
        'start_hour1',
        'start_hour2',
        'tolerance_start',
        'end_hour1',
        'end_hour2',
        'tolerance_end',
        'note'
    )
    return data


def leave_log_ids(user):
    """
    Fetch all logs from an user
    user->int
    """
    today = datetime.now().strftime("%Y-%m-%d")
    data = Request_leave_log.objects.filter(
        user__id=user,
        date__gt=today,
        active=True,
    )
    return data


def start_or_end(log, shift):
    """
    Determine if wish is to change start or end hour
    and if it start/end from or between
    log->exchange.models.Request_shift_log
    shift->calendrier.models.Shift
    return tuple. 1st item is start/end. 2nd From/Between
    """
    condition = 0
    condition += bool(log.start_hour1)
    condition += bool(log.start_hour2)
    condition += 3 if log.end_hour1 else 0
    condition += 3 if log.end_hour2 else 0
    tolerance_start = log.tolerance_start
    tolerance_end = log.tolerance_end
    start = log.start_hour1 if log.start_hour1 else log.start_hour2
    end = log.end_hour1 if log.end_hour1 else log.end_hour2
    match condition:
        case 1:
            # Check service entry. From
            start1 = (datetime.combine(
                shift.date, start)-tolerance_start).time()
            if shift.start_hour and shift.start_hour < start1:
                print("remove shift prout")
                # Tested and it works
                Request_shift.objects.filter(
                    giver_shift_id=shift.id,
                    request_id=log.id
                ).delete()
        case 2:
            # Check service entry. Between
            start1 = (datetime.combine(
                shift.date, log.start_hour1)-tolerance_start).time()
            start2 = (datetime.combine(
                shift.date, log.start_hour2)+tolerance_start).time()
            if shift.start_hour:
                if not start1 < shift.start_hour < start2:
                    print("remove shift from exchange_request_shift")
                    # To be tested
                    # Request_shift.objects.filter(
                    #     giver_shift_id=shift['id'],
                    #     request_id=log['id']
                    # ).delete()
        case 3:
            # Check end of service. From
            end1 = (datetime.combine(shift.date, end)-tolerance_end).time()
            if shift.end_hour and shift.end_hour > end1:
                print("remove shift from exchange_request_shift")
                # To be tested
                # Request_shift.objects.filter(
                #     giver_shift_id=shift['id'],
                #     request_id=log['id']
                # ).delete()
        case 6:
            # Check end of service. Between
            end1 = (datetime.combine(
                shift.date, log.end_hour1)-tolerance_start).time()
            end2 = (datetime.combine(
                shift.date, log.end_hour2)+tolerance_start).time()
            if shift.end_hour and not end1 < shift.end_hour < end2:
                print("remove shift from exchange_request_shift")
                # To be tested
                # Request_shift.objects.filter(
                #     giver_shift_id=shift['id'],
                #     request_id=log['id']
                # ).delete()
        case 4:
            # Check start and end of service. Between
            start1 = (datetime.combine(
                shift.date, start)-tolerance_start).time()
            end1 = (datetime.combine(
                shift.date, end)-tolerance_end).time()
            if shift.start_hour and shift.end_hour:
                if shift.start_hour < start1 and shift.end_hour < end1:
                    print("remove shift from exchange_request_shift")
                    # To be tested
                    # Request_shift.objects.filter(
                    #     giver_shift_id=shift['id'],
                    #     request_id=log['id']
                    # ).delete()


def all_shifts(date, query, excluded):
    """Find all shifts from a choosen user
    date->datetime.date
    query->dict
    excluded->list with int
    return a django.db.models.query.QuerySet
    """
    shifts = Shift.objects.filter(
        Q(**query)
        | Q(date=date,
            shift_name__iregex=(r'^200'))
    ).exclude(
        id__in=excluded,
    ).values(
        'id',
        'shift_name',
        'start_hour',
        'end_hour'
    )
    return shifts


def update_shift(log, shift):
    """
    Retrieve user's shift and check if it's still corresponding
    log->exchange.models.Request_shift_log
    shift->exchange.models.Request_shift
    """
    # Retrieve user's shift
    giver_shift = Shift.objects.get(id=shift.giver_shift.id)
    # Remove if timetable no longer corresponds to wish
    start_or_end(log, giver_shift)
    # Remove if it's not a shift anymore
    if not re.search("^[0-9]", giver_shift.shift_name):
        print("Shift has changed. To be removed")
        # To be tested
        # Request_shift.objects.filter(
        #     giver_shift=shift.giver_shift,
        #     request_id=log['id']
        # ).delete()
