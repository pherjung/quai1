# from django.shortcuts import render
from django.views import generic
from django.utils.html import format_html, mark_safe
import datetime
import calendar

from .models import Shift
from .utils import Calendar


class CalendarView(generic.ListView):
    model = Shift
    template_name = 'calendrier/body.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = get_date(self.request.GET.get('month', None))
        cal = Calendar(date.year, date.month)
        html_cal = mark_safe(cal.formatmonth(withyear=True))
        context['calendar'] = format_html(html_cal)
        context['next_month'] = next_month(date)
        context['prev_month'] = prev_month(date)
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)

    return datetime.datetime.today()
