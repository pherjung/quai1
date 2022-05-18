import sys
import os
from datetime import date, datetime, timedelta
import django
import vobject
import requests

sys.path.append('./../../quai1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quai1.settings')
django.setup()

from login.models import CustomUser
from calendrier.models import Shift
from exchange.models import Request_shift, Request_shift_log, Request_leave, Request_leave_log
from calendarManager.update import all_shifts, update_shift
from exchange.update_shift import search_shifts, search_wishes
from django.db.utils import OperationalError

users = CustomUser.objects.all()
LEAVES = ('RT', 'RTT', 'CT', 'CTT')


def lang(url_raw):
    """
    Change language to French
    url_raw->str
    """
    url = url_raw.split('&')[0]
    request = requests.get(f"{url}&sprache=fr")
    return request


def write_data(user):
    """
    Update or create calendar
    user->dict
    """
    request = lang(user.url)
    request.encoding = request.apparent_encoding
    cal = vobject.readOne(request.text)
    events = cal.getSortedChildren()
    today = datetime.now()
    batch = []

    for entry in events:
        if entry.name == 'VEVENT':
            start = entry.getChildValue('dtstart')
            dtst = datetime(year=start.year,
                            month=start.month,
                            day=start.day)
            end = entry.getChildValue('dtend')
            # Do not apply events before today
            if dtst < today:
                continue

            event_id = f"{start.strftime('%Y-%m-%d')}_{user.username}"
            shift_name = entry.getChildValue('summary').split(': ')[1]
            begin = start if isinstance(start, datetime) else None
            ende = end if isinstance(end, datetime) else None

            values = {'shift_id': event_id,
                      'shift_name': shift_name,
                      'date': start.strftime('%Y-%m-%d'),
                      'start_hour': begin,
                      'end_hour': ende,
                      'owner': user,
                      }
            if isinstance(start, datetime):
                batch.append(Shift(**values))
            # Some holidays are only "one" event
            else:
                while start < end:
                    values['shift_id'] = f"{start.strftime('%Y-%m-%d')}_{user.username}"
                    values['date'] = start.strftime('%Y-%m-%d')
                    batch.append(Shift(**values))
                    start += timedelta(1)

    Shift.objects.bulk_update_or_create(batch,
                                        ['start_hour', 'end_hour'],
                                        match_field='shift_id')


def update_shifts(user_id, request_shift_logs):
    """
    Check if shift (still) corresponds to the need. Update if necessary
    user_id->int
    request_shift_logs->django.db.models.query.QuerySet
    """
    for log in request_shift_logs:
        exchange = Request_shift.objects.filter(request_id=log.id)
        excluded = []
        query = search_shifts(log, log.date, False)
        user_shift = Shift.objects.get(owner=user_id, date=log.date)
        for req in exchange:
            excluded.append(req.giver_shift.id)
            update_shift(log, req)
        # Submit new shifts as exchange
        new_shifts = all_shifts(log.date, query, excluded, user_id)
        for shift in new_shifts:
            Request_shift.objects.get_or_create(
                user_shift=user_shift,
                giver_shift=shift,
                note=log.note,
                request=log
            )


def update_leave(username, request_leave_logs):
    """
    Update leaves
    username->str
    request_leave_logs->django.db.models.query.QuerySet
    """
    for log in request_leave_logs:
        user_shift = Shift.objects.get(date=log.date, owner__username=username)
        # Remove wish if user's shift is now a leave
        if user_shift.shift_name in LEAVES:
            Request_leave_log.objects.filter(user__username=username,
                                             date=log.date).delete()
            Request_leave.objects.filter(request=log.id).delete()
            continue
        # Remove wish if giver's shift isn't a leave anymore
        leaves_wishes = Request_leave.objects.filter(request=log.id)
        for req in leaves_wishes:
            if req.giver_shift.shift_name not in LEAVES:
                req.delete()
        search_wishes(username, log, user_shift)


def apply(user):
    """
    apply update
    user->
    """
    today = datetime.now()
    shifts_log = Request_shift_log.objects.filter(
        user__id=user.id,
        date__gt=today,
        active=True,
    )
    update_shifts(user.id, shifts_log)
    leaves_log = Request_leave_log.objects.filter(
        user=user.id,
        date__gt=today,
        active=True,
    )
    update_leave(user.username, leaves_log)


try:
    # First update all calendars
    for who in users:
        write_data(who)

    # Then check if there are differences
    for who in users:
        apply(who)
except OperationalError:
    pass
