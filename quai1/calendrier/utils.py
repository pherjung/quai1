from calendar import HTMLCalendar
from .models import Shift


class Calendar(HTMLCalendar):
    def __init__(self, request, year=None, month=None):
        self.user = request.user
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, shift):
        shift_per_day = shift.filter(date__day=day,
                                     owner=self.user)
        cell = ''
        for shift in shift_per_day:
            cell += f'<p>{shift.shift_name}</p>'
            cell += f'<p>{shift.start_hour}</p>'
            cell += f'<p>{shift.end_hour} </p>'

        if day != 0:
            return f"<td onclick=myFunction('calendar');myFunction('box')><div class='date'>{day}</div>{cell}</td>"

        return '<td></td>'

    def formatweek(self, theweek, shifts):
        week = ''
        for day, weekday in theweek:
            week += self.formatday(day, shifts)

        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        shifts = Shift.objects.filter(date__year=self.year,
                                      date__month=self.month)
        cal = '<table class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, shifts)}\n"

        cal += '</table>'
        return cal
