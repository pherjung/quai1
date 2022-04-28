import sys
import os
import django
from ics import Calendar
import requests
import arrow

sys.path.append('./../../quai1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quai1.settings')
django.setup()

from login.models import CustomUser
from calendrier.models import Shift
from exchange.models import Request_shift, Request_leave, Request_leave_log
from calendarManager.update import shift_log_ids, all_shifts, update_shift, leave_log_ids
from exchange.update_shift import search_shifts, search_wishes

users = CustomUser.objects.all().values('id', 'username', 'url')
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
    request = lang(user['url'])
    request.encoding = request.apparent_encoding
    cal = Calendar(request.text)
    events = cal.timeline.start_after(arrow.now())

    for entry in events:
        event_id = entry.begin.format('YYYY-MM-DD')+'_'+user['username']
        if entry.begin.format('HH:mm') == entry.end.format('HH:mm'):
            begin = None
            end = None
        else:
            begin = entry.begin.format('HH:mm:ss')
            end = entry.end.format('HH:mm:ss')

        values = {'shift_name': entry.name.split(': ')[1],
                  'date': entry.begin.format('YYYY-MM-DD'),
                  'start_hour': begin,
                  'end_hour': end,
                  'owner_id': user['id']
                  }
        Shift.objects.update_or_create(
            shift_id=event_id,
            defaults=values
        )


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
            print("debug: user's shift isn't anymore a leave. Remove wish")
            continue
        # Remove wish if giver's shift isn't a leave anymore
        leaves_wishes = Request_leave.objects.filter(request=log.id)
        for req in leaves_wishes:
            if req.giver_shift.shift_name not in LEAVES:
                req.delete()
                print("debug: giver's shift isn't anymore a leave. Remove")
        search_wishes(username, log, user_shift)

for who in users:
    write_data(who)
    shifts_log = shift_log_ids(who['id'])
    update_shifts(who['id'], shifts_log)
    leaves_log = leave_log_ids(who['id'])
    update_leave(who['username'], leaves_log)
