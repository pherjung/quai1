# from django.shortcuts import render
from django.views import generic
from django.utils.html import format_html, mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
import calendar

from .models import Shift
from .utils import Calendar
from exchange.forms import RestForms, AskRestForms


class CalendarView(LoginRequiredMixin, generic.ListView):
    model = Shift
    template_name = 'calendrier/body.html'
    login_url = '/accounts/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = get_date(self.request.GET.get('month', None))
        cal = Calendar(self.request, date.year, date.month)
        html_cal = mark_safe(cal.formatmonth(withyear=True))
        context['calendar'] = format_html(html_cal)
        context['next_month'] = next_month(date)
        context['prev_month'] = prev_month(date)
        context['form'] = RestForms()
        context['shift_form'] = AskRestForms()
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)

    return datetime.datetime.today()


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + datetime.timedelta(days=1)
    month = 'month='+str(next_month.year)+'-'+str(next_month.month)
    return month


def prev_month(d):
    first = d.replace(day=1)
    next_month = first - datetime.timedelta(days=1)
    month = 'month='+str(next_month.year)+'-'+str(next_month.month)
    return month
