from datetime import datetime, timedelta
from calendar import Calendar, monthrange
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from exchange.forms import LeaveForms, RequestLeaveForms
from .models import Shift


def monthly_calendar(request):
    events = []
    cal = Calendar(0)
    datum = get_date(request.GET.get('month', None))
    month_days = cal.monthdatescalendar(datum.year, datum.month)
    shifts = Shift.objects.filter(owner=request.user,
                                  date__range=[month_days[0][0],
                                               month_days[-1][-1]])
    for week in month_days:
        week_events = []
        for day in week:
            try:
                shift = shifts.get(date=day)
                if shift.date.month == datum.month:
                    week_events += [[day, shift]]
                else:
                    week_events += [[None, None]]
            except Shift.DoesNotExist:
                week_events += [[None, None]]

        events.append(week_events)
    context = {'events': events,
               'full_date': datum,
               'next_month': next_month(datum)}
    return context


@login_required
def view_calendar(request):
    context = monthly_calendar(request)
    context['form'] = LeaveForms()
    context['shift_form'] = RequestLeaveForms()
    return render(request, 'calendrier/body.html', context)


def get_date(date):
    if date:
        year, month = (int(value) for value in date.split('-'))
        return datetime(year=year, month=month, day=1)

    now = datetime.today().replace(day=1, hour=5, minute=30)
    return now


def next_month(date):
    days_month = monthrange(date.year, date.month)[1]
    coming_date = date + timedelta(days=days_month)
    return coming_date.year, coming_date.month


@login_required
def values(request):
    context = monthly_calendar(request)
    return render(request, 'calendrier/cal.html', context)
