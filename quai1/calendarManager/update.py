from datetime import datetime, timedelta
from django.db.models import Q
import re

from calendrier.models import Shift
from exchange.models import Request_log, Request_shift


def log_ids(user):
    """
    Fetch all logs from a user
    user->int
    return a QuerySet with dict
    """
    today = datetime.now().strftime("%Y-%m-%d")
    data = Request_log.objects.filter(
        user_id=user,
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


def start_or_end(log, shift):
    """
    Determine if wish is to change start or end hour
    and if it start/end from or between
    log->list
    return tuple. 1st item is start/end. 2nd From/Between
    """
    condition = 0
    condition += bool(log['start_hour1'])
    condition += bool(log['start_hour2'])
    condition += 3 if log['end_hour1'] else 0
    condition += 3 if log['end_hour2'] else 0
    tolerance_start = log['tolerance_start']
    tolerance_end = log['tolerance_end']
    start = log['start_hour1'] if log['start_hour1'] else log['start_hour2']
    end = log['end_hour1'] if log['end_hour1'] else log['end_hour2']
    match condition:
        case 1:
            # Check service entry. From
            start1 = (datetime.combine(
                shift['date'], start)-tolerance_start).time()
            if shift['start_hour'] and shift['start_hour'] < start1:
                print("remove shift prout")
                # Tested and it works
                Request_shift.objects.filter(
                    giver_shift_id=shift['id'],
                    request_id=log['id']
                ).delete()
        case 2:
            # Check service entry. Between
            start1 = (datetime.combine(
                shift['date'], log['start_hour1'])-tolerance_start).time()
            start2 = (datetime.combine(
                shift['date'], log['start_hour2'])+tolerance_start).time()
            if shift['start_hour']:
                if not start1 < shift['start_hour'] < start2:
                    print("remove shift from exchange_request_shift")
                    # To be tested
                    # Request_shift.objects.filter(
                    #     giver_shift_id=shift['id'],
                    #     request_id=log['id']
                    # ).delete()
        case 3:
            # Check end of service. From
            end1 = (datetime.combine(
                shift['date'], end)-tolerance_end).time()
            if shift['end_hour'] and shift['end_hour'] < end1:
                print("remove shift from exchange_request_shift")
                # To be tested
                # Request_shift.objects.filter(
                #     giver_shift_id=shift['id'],
                #     request_id=log['id']
                # ).delete()
        case 6:
            # Check end of service. Between
            end1 = (datetime.combine(
                shift['date'], log['end_hour1'])-tolerance_start).time()
            end2 = (datetime.combine(
                shift['date'], log['end_hour2'])+tolerance_start).time()
            if shift['end_hour'] and not end1 < shift['end_hour'] < end2:
                print("remove shift from exchange_request_shift")
                # To be tested
                # Request_shift.objects.filter(
                #     giver_shift_id=shift['id'],
                #     request_id=log['id']
                # ).delete()
        case 4:
            # Check start and end of service. Between
            start1 = (datetime.combine(
                shift['date'], start)-tolerance_start).time()
            end1 = (datetime.combine(
                shift['date'], end)-tolerance_end).time()
            if shift['start_hour'] and shift['end_hour']:
                if shift['start_hour'] < start1 and shift['end_hour'] < end1:
                    print("remove shift from exchange_request_shift")
                    # To be tested
                    # Request_shift.objects.filter(
                    #     giver_shift_id=shift['id'],
                    #     request_id=log['id']
                    # ).delete()


def all_shifts(owner_id, date, query, excluded):
    """Find all shifts from a choosen user
    owner_id->int
    date->datetime.datetime
    query->dict
    excluded->list with int
    return a QuerySet with dict
    """
    shifts = Shift.objects.filter(
        Q(**query)
        | Q(date=date,
            shift_name__iregex=(r'^200'))
    ).exclude(
        Q(id__in=excluded) | Q(owner=owner_id)
    ).values(
        'id',
        'shift_name',
        'start_hour',
        'end_hour'
    )
    return shifts


def shifts_to_change(log_id):
    """
    From log, retrieve all shifts corresponding to the request
    log_id->int
    return a QuerySet with dict
    """
    shifts = Request_shift.objects.filter(
        request_id=log_id
    ).values(
        'id',
        'giver_shift_id',
        'user_shift_id',
        'request_id'
    )
    return shifts


def update_shift(log, shift_id):
    """
    Retrieve user's shift and check if it's still corresponding
    log->list
    shifts->list of tuple
    """
    # Retrieve user's shift
    giver_shift = Shift.objects.get(id=shift_id)
    # Remove if timetable no longer corresponds to wish
    start_or_end(log, giver_shift)
    # Remove if it's not a shift anymore
    if not re.search("^[0-9]", giver_shift.shift_name):
        print("Shift has changed. To be removed")
        # To be tested
        # Request_shift.objects.filter(
        #     giver_shift=shift_id,
        #     request_id=log['id']
        # ).delete()
