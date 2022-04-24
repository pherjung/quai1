import sys
import os
import django
from ics import Calendar
import requests
import arrow

sys.path.append('/home/pherjung/projet/cff/quai1++/quai1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quai1.settings')
django.setup()

from login.models import CustomUser
from calendrier.models import Shift
from exchange.models import Request_shift
from calendarManager.update import log_ids, all_shifts, shifts_to_change, update_shift
from exchange.update_shift import search_shifts

users_url = CustomUser.objects.all().values('id',
                                            'username',
                                            'url')


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


for who in users_url:
    write_data(who)
    log = log_ids(who['id'])
    for i in log:
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
