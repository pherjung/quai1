from datetime import datetime, time, timedelta as td
from calendrier.models import Shift


def define_art(shift):
    """
    shift->shift object
    Return a string. Define which art of shift it is
    """
    if shift.start_hour:
        start = shift.start_hour.time()
        end = shift.end_hour.time()
    else:
        return None

    # middle shift. Starts at 06:00 or ends at 20:00
    if start >= time(6) and end <= time(20):
        art_shift = 'middle'

    # evening shift. Ends between 20:00 and 00:00
    if time(20) < end <= time(23, 59) or end == time():
        art_shift = 'evening'

    # night shift starts or ends between 00:01 and 03:59
    if time(0) < start < time(4):
        art_shift = 'night-start'
    if end < time(4):
        art_shift = 'night-end'

    # morning shift starts between 04:00 and 06:00 or ends at 05:00
    if time(4) <= start <= time(6):
        art_shift = 'morning'
    if time(4) < end < time(5):
        art_shift = 'morning'

    return art_shift


def find_2serie(last, date, username):
    """
    Find previous/next leave
    last->Boolean
    date->datetime.date
    username->str
    return calendar Shift model
    """
    i = 1
    serie = 0
    leaves = ('RT', 'RTT', 'CT', 'CT', 'F', 'CTS')
    while True:
        a = 1
        new_date = date-td(days=i) if last else date+td(days=i)
        try:
            day = Shift.objects.get(date=new_date,
                                    owner__username=username)
        except Shift.DoesNotExist:
            i += 1
            continue
        if day.shift_name in leaves:
            while True:
                new_date = date-td(days=i+a) if last else date+td(days=i+a)
                try:
                    leave_day = Shift.objects.get(date=new_date,
                                                  owner__username=username)
                except Shift.DoesNotExist:
                    a += 1
                    continue
                if leave_day.start_hour or leave_day.shift_name == '200':
                    serie += 1
                    i += a
                    break
                a += 1

        if serie == 2:
            return day

        i += 1


def find(last, date, username):
    """
    Find previous/next working day
    last->Boolean
    date->datetime.date
    username->str
    return calendar Shift model
    """
    serie = find_2serie(last, date, username)
    start_date = date
    increment = 1
    while start_date != serie.date:
        new_date = date-td(days=increment) if last else date+td(days=increment)
        try:
            day = Shift.objects.get(date=new_date,
                                    owner__username=username)
        except Shift.DoesNotExist:
            increment += 1
            continue
        if day.end_hour:
            art = define_art(day)
            return day, increment, art
        # In case no work date is found
        if day.shift_name == '200':
            return serie, 0, None

        # In case next day are leaves
        increment += 1
        start_date = start_date-td(1) if last else start_date+td(1)


def horary(last, datum, username):
    """
    Search start/end hour
    last->Boolean
    search_day->calendrier.models.Shift
    datum->datetime.date
    username->str
    return datetime.datetime object
    """
    work_day = find(last, datum, username)
    work_end = work_day[0].end_hour
    start_raw = work_end if last else work_day[0].start_hour
    day = datum.day
    hours = 12 if last else -12
    match work_day[1]:
        case 0:
            if last:
                hours = 0
                start_raw = datetime.combine(datum, time())
            else:
                day += 1
                start_raw = datetime.combine(datum, time(12))
        case 1:
            if last and work_day[2] in ['night-start', 'morning']:
                hours = 0
                start_raw = start_raw.replace(hour=0, minute=0)
        case 2:
            if last:
                leave = work_day[0].date+td(1)
            else:
                leave = work_day[0].date-td(1)

            leave = Shift.objects.get(owner__username=username,
                                      date=leave).shift_name

            if leave in ['RT', 'RTT', 'RTV']:
                if last and work_end.time() <= time(12):
                    hours = 0
                    start_raw = start_raw.replace(hour=0, minute=0)
                elif start_raw.date() == work_day[0].start_hour.date():
                    day += 1

            else:
                if last:
                    if work_day[0].start_hour.date() == work_end.date():
                        start_raw = start_raw.replace(hour=0, minute=0)
                        hours = 0
                else:
                    day += 1
        case _:
            hours = 9 if last else -9
            buffer = work_day[0].start_hour+td(hours=hours)
            if last and buffer.date() == work_day[0].start_hour.date():
                start_raw = start_raw.replace(hour=0, minute=0)
                hours = 0

    start_raw += td(hours=hours)
    start_raw = start_raw.replace(datum.year, datum.month, day)
    return start_raw


def start_end_hour(datum, username):
    """
    date->datetime.date
    username->str
    return a dict with 2 datetime.time objects
    """
    horary_range = {'start_hour': horary(True, datum, username),
                    'end_hour': horary(False, datum, username)}
    return horary_range
