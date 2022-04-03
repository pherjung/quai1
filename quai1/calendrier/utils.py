from datetime import datetime
from calendar import HTMLCalendar
from .models import Shift


class Calendar(HTMLCalendar):
    def __init__(self, request, year=None, month=None):
        self.user = request.user
        self.year = year
        self.month = month
        super().__init__()

    def formatday(self, day, shift):
        shift_per_day = shift.filter(date__day=day,
                                     owner=self.user)
        cell = ''
        for shift_day in shift_per_day:
            info = f"class={shift_day.shift_name} id ='shift'"
            cell += f"<p {info}>{shift_day.shift_name}</p>"
            cell += f'<p>{shift_day.start_hour}</p>'
            cell += f'<p>{shift_day.end_hour} </p>'

        if day != 0:
            date_obj = datetime(self.year, self.month, day)
            day_name = date_obj.strftime("%A")
            month_name = date_obj.strftime("%B")
            class_date = f"{day_name}_{day}_{month_name}_{self.year}"
            date_cell = f"<div class='date'>{day}</div>{cell}"
            param = f"class={class_date} onclick=\"displayBlock(this, 'calendar')\""
            return f"<td {param}>{date_cell}</td>"

        return '<td></td>'

    def formatweek(self, theweek, shifts):
        week = ''
        for day in theweek:
            week += self.formatday(day[0], shifts)

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
