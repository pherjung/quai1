from datetime import datetime, timedelta
from calendar import Calendar, monthrange
from django.shortcuts import render
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from exchange.forms import LeaveForms, RequestLeaveForms
from exchange import models as wish
from .models import Shift


def monthly_calendar(request):
    events = []
    datum = get_date(request.GET.get('month', None))
    month_days = Calendar(0).monthdatescalendar(datum.year, datum.month)
    shifts = Shift.objects.filter(owner=request.user,
                                  date__range=[month_days[0][0],
                                               month_days[-1][-1]]
                                  ).values('date', 'shift_name',
                                           'start_hour', 'end_hour')
    # User ask for help
    asked_leaves = wish.Request_leave_log.objects.filter(
        user=request.user,
        date__range=[month_days[0][0],
                     month_days[-1][-1]],
        active=True).values_list('id')
    asked_shifts = wish.Request_shift_log.objects.filter(
        user=request.user,
        date__range=[month_days[0][0],
                     month_days[-1][-1]],
        active=True).values_list('id')
    # User can help or has an accepted swap offer
    work = wish.Request_shift.objects.filter(
        Q(user_shift__owner=request.user) | Q(giver_shift__owner=request.user),
        request__date__range=[month_days[0][0],
                              month_days[-1][-1]],
    ).values_list('accepted', 'confirmed',
                  'giver_shift__start_hour',
                  'giver_shift__end_hour',
                  'user_shift__start_hour',
                  'user_shift__end_hour')
    leaves = wish.Request_leave.objects.filter(
        Q(user_shift__owner=request.user) | Q(giver_shift__owner=request.user),
        request__date__range=[month_days[0][0],
                              month_days[-1][-1]],
    ).values_list('validated', 'user_shift__shift_name')
    for week in month_days:
        week_events = []
        for day in week:
            validated = swaped = top_div = bottom_div = None
            accepted = swaped_leave = swaped_shift = validated_shift = validated_leave = False
            try:
                shift = shifts.get(date=day)
                if shift['date'].month == datum.month:
                    # User ask for help
                    div_leave = asked_leaves.filter(date=day)
                    div_shift = asked_shifts.filter(date=day)
                    top_div = 'wish' if div_leave or div_shift else 'default'
                    # User can help
                    swap_shift = work.filter(request__date=day,
                                             giver_shift__owner=request.user,
                                             accepted=None)
                    swap_leave = leaves.filter(request__date=day,
                                               giver_shift__owner=request.user,
                                               accepted=None)
                    bottom_div = 'swap' if swap_shift or swap_leave else 'default-swap'
                    # Accepted swap offer - shift
                    ok_shift_asker = work.filter(request__date=day,
                                                 request__user=request.user,
                                                 accepted=True)
                    ok_shift_giver = work.filter(request__date=day,
                                                 giver_shift__owner=request.user,
                                                 accepted=True).values_list('confirmed')
                    # Mandatory because filter is used instead of get
                    if ok_shift_asker or ok_shift_giver:
                        accepted = 'fa-envelope'
                        validated_shift = work.filter(request__date=day,
                                                      confirmed=True)
                        # Check if swap is applied
                        if validated_shift:
                            accepted = 'fa-arrow-right-arrow-left'
                            hours = work.filter(request__date=day,
                                                confirmed=True)
                            if hours:
                                swaped_shift = hours[0][2:4] == hours[0][4:]

                    # Accepted swap offer - leave
                    ok_leave_asker = leaves.filter(request__date=day,
                                                   request__user=request.user,
                                                   accepted=True)
                    ok_leave_giver = leaves.filter(request__date=day,
                                                   giver_shift__owner=request.user,
                                                   accepted=True)
                    # Mandatory because filter is used instead of get
                    if ok_leave_asker or ok_leave_giver:
                        accepted = 'fa-envelope'
                        validated_leave = leaves.filter(request__date=day,
                                                        validated=True)
                        # Check if swap is applied
                        if validated_leave:
                            accepted = 'fa-arrow-right-arrow-left'
                            swaped_leave = validated_leave[0][1] in ['RT', 'CT', 'CTT', 'RTT', 'CTS']

                    validated = validated_shift or validated_leave
                    top_div = 'wish_accepted' if validated else top_div
                    swaped = 'green' if swaped_shift or swaped_leave else 'red'
                    if len(ok_shift_giver) > 0:
                        if not ok_shift_giver[0]:
                            top_div = 'helping'
                            accepted = 'fa-clock'

                    if len(ok_leave_giver):
                        if not ok_leave_giver[0]:
                            top_div = 'helping'
                            accepted = 'fa-clock'
                else:
                    shift = None
            except Shift.DoesNotExist:
                shift = None
            week_events += [[shift, accepted, validated, swaped,
                             top_div, bottom_div]]

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
