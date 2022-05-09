from datetime import timedelta, datetime, time
from calendrier.models import Shift


# Ne fonctionne pas avec les tours du matin
# Ne fonctionne pas avec les tours 200
def start_end_hour(date, username):
    """
    date->datetime.date
    username->str
    hours->int
    return a dict with 2 datetime.time objects
    """
    # Find last working day
    def find(position):
        """
        Find previous/next working day
        position->Boolean
        return calendar Shift model
        """
        increment = 1
        while True:
            changed_date = timedelta(days=increment)
            # Previous day
            if position:
                day = Shift.objects.get(date=date-changed_date,
                                        owner__username=username)
            # Next day
            else:
                day = Shift.objects.get(date=date+changed_date,
                                        owner__username=username)

            if day.end_hour or day.shift_name == 200:
                return day, increment

            increment += 1

    last_day = find(True)
    next_day = find(False)

    def horary(position, search_day):
        """
        Return datetime.time object
        position->Boolean
        search_day->
        return
        """
        match search_day[1]:
            # Avec codécision si tour de repos entre 2 tours
            case 1:
                hour = 10
            case 2:
                if position:
                    name = search_day[0].date+timedelta(1)
                else:
                    name = search_day[0].date-timedelta(1)

                # Avec codécision si un RT sec
                if name in ['RT', 'RTT', 'RTV']:
                    hour = 12
                # Si CT isolé
                else:
                    hour = 0
            # Si plusieurs congés avec codécision
            case _:
                hour = 8

        if search_day[0].shift_name != 200:
            if position:
                start_raw = datetime.combine(search_day[0].date,
                                             search_day[0].end_hour)+timedelta(hours=hour)
            else:
                start_raw = datetime.combine(search_day[0].date,
                                             search_day[0].start_hour)-timedelta(hours=hour)
        else:
            if position:
                start_raw = search_day.end_hour
            else:
                start_raw = search_day.start_hour

        return time(hour=start_raw.hour, minute=start_raw.minute)

    horary_range = {'start_hour': horary(True, last_day),
                    'end_hour': horary(False, next_day)}

    return horary_range
