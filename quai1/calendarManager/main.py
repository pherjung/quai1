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
from calendarManager.update import shift_log_ids, all_shifts, shifts_to_change, update_shift, leave_log_ids
from exchange.update_shift import search_shifts, search_wishes

users = CustomUser.objects.all().values('id', 'username', 'url')
LEAVES = ('RT', 'RTT', 'CT', 'CTT')


def lang(url_raw):
    "Change language to French"
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


for who in users:
    write_data(who)
    # Update schedule
    shifts_log = shift_log_ids(who['id'])
    for i in shifts_log:
        excluded = [who['id']]
        exchange = shifts_to_change(i['id'])
        query = search_shifts(i, i['date'], False)
        for a in exchange:
            excluded.append(a['giver_shift_id'])
            update_shift(i, a['giver_shift_id'])
        # Submit new shifts as exchange
        new_shifts = all_shifts(i['date'], query, excluded)
        for p in new_shifts:
            Request_shift.objects.create(
                user_shift=i['user_shift_id'],
                giver_shift=p['id'],
                note=i['note'],
                request=i['id']
            )
    # Update leaves
    leaves_log = leave_log_ids(who['id'])
    for a in leaves_log:
        user_shift = Shift.objects.get(date=a.date, owner__id=who['id'])
        # Remove wish if user's shift is now a leave
        if user_shift.shift_name in LEAVES:
            Request_leave_log.objects.filter(user=who['id'],
                                             date=a.date).delete()
            Request_leave.objects.filter(request=a.id).delete()
            print("debug: user's shift isn't anymore a leave. Remove wish")
            continue
        # Remove wish if giver's shift isn't a leave anymore
        leaves_wishes = Request_leave.objects.filter(request=a.id)
        for c in leaves_wishes:
            if c.giver_shift.shift_name not in LEAVES:
                c.delete()
                print("debug: giver's shift isn't anymore a leave. Remove")
        search_wishes(who['id'], a, user_shift)
