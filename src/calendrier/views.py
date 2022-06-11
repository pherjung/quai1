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
                                               month_days[-1][-1]])
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
    # User can help
    swap_shifts = wish.Request_shift.objects.filter(
        giver_shift__owner=request.user,
        giver_shift__date__range=[month_days[0][0],
                                  month_days[-1][-1]],
        accepted=None,
        confirmed=False,
    )
    swap_leaves = wish.Request_leave.objects.filter(
        giver_shift__owner=request.user,
        giver_shift__date__range=[month_days[0][0],
                                  month_days[-1][-1]],
        accepted=None,
        validated=False,
    )
    # Accepted swap offer
    accepted_shifts = wish.Request_shift.objects.filter(
        Q(user_shift__owner=request.user) | Q(giver_shift__owner=request.user),
        request__date__range=[month_days[0][0],
                              month_days[-1][-1]],
        accepted=True,
    ).values_list('accepted', 'confirmed',
                  'giver_shift__start_hour',
                  'giver_shift__end_hour',
                  'user_shift__start_hour',
                  'user_shift__end_hour')
    accepted_leaves = wish.Request_leave.objects.filter(
        Q(user_shift__owner=request.user) | Q(giver_shift__owner=request.user),
        request__date__range=[month_days[0][0],
                              month_days[-1][-1]],
        accepted=True,
    ).values_list('validated', 'user_shift__shift_name')
    for week in month_days:
        week_events = []
        for day in week:
            try:
                shift = shifts.get(date=day)
                if shift.date.month == datum.month:
                    # User ask for help
                    div_leave = bool(asked_leaves.filter(date=day))
                    div_shift = bool(asked_shifts.filter(date=day))
                    top_div = 'wish' if div_leave or div_shift else 'default'
                    # User can help
                    swap_shift = bool(swap_shifts.filter(request__date=day))
                    swap_leave = bool(swap_leaves.filter(request__date=day))
                    bottom_div = 'swap' if swap_shift or swap_leave else 'default-swap'
                    # Accepted swap offer - shift
                    accepted_shift_asker = bool(
                        accepted_shifts.filter(request__date=day,
                                               request__user=request.user))
                    accepted_shift_giver = bool(
                        accepted_shifts.filter(request__date=day,
                                               giver_shift__owner=request.user))
                    swaped_leave = swaped_shift = validated_shift = validated_leave = False
                    if accepted_shift_asker or accepted_shift_giver:
                        validated_shift = bool(
                            accepted_shifts.filter(request__date=day,
                                                   confirmed=True))
                        # Check if swap is applied
                        if validated_shift:
                            hours = accepted_shifts.get(request__date=day,
                                                        confirmed=True)
                            swaped_shift = bool(hours[2:4] == hours[4:])

                    # Accepted swap offer - leave
                    accepted_leave = bool(accepted_leaves.filter(request__date=day))
                    if accepted_leave:
                        validated_leave = accepted_leaves.get(request__date=day)
                        # Check if swap is applied
                        swaped_leave = bool(validated_leave[1] in ['RT', 'CT', 'CTT', 'RTT'])
                    accepted = bool(accepted_shift_giver or accepted_shift_asker or accepted_leave)
                    top_div = 'wish_accepted' if accepted else top_div
                    validated = bool(validated_shift or validated_leave)
                    top_div = 'helping' if accepted_shift_giver and not validated else top_div
                    swaped = bool(swaped_shift or swaped_leave)

                    week_events += [[day, shift, accepted, validated,
                                     swaped, top_div, bottom_div]]
                else:
                    week_events += [[None, None, None, None, None, None, None]]
            except Shift.DoesNotExist:
                week_events += [[None, None, None, None, None, None, None]]

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
