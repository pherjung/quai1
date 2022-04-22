import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.template.defaulttags import register
from django.db.models import Q
from exchange.models import Request_leave, Give_leave, Request_shift
from .forms import AcceptDeclineDateForm, DeleteForm, AcceptDeclineForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@login_required
def exchanges(request):
    # Gifted leaves
    gifts = Give_leave.objects.filter(
        shift__owner__username=request.user,
        given=False,
    ).values_list(
        'shift',
        'shift__date',
    ).exclude(shift__date__lt=(datetime.datetime.now()))
    gifts_form = {}
    for item in gifts:
        gifts_form[item[0]] = DeleteForm(leave_id=item[0])

    # Given leaves
    accepted_leaves = Request_leave.objects.filter(
        giver_shift_id__owner__username=request.user,
        accepted=True,
    ).values_list(
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'user_shift__owner__first_name',
        'user_shift__owner__last_name',
        'note',
        'given_leave__date',
    ).exclude(user_shift__date__lt=(datetime.datetime.now()))

    # Requested leaves
    requester_ids = set()
    # Recover all the leave the connected user can exchange
    request_leaves = Request_leave.objects.filter(
        giver_shift_id__owner__username=request.user,
        user_shift__date__gt=(datetime.datetime.now()),
        accepted=None,
    ).values_list(
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'user_shift__owner',
        'user_shift__owner__username',
        'note',
        'validated',
        'user_shift')

    leaves = 0
    while leaves < len(request_leaves):
        # Recover all requesters
        requester_ids.add(request_leaves[leaves][4])
        leaves += 1

    given_leaves = {}
    for i in requester_ids:
        dates = Give_leave.objects.filter(
            shift__owner=i,
            given=False
        ).values_list(
            'shift',
            'shift__date'
        ).exclude(shift__date__lt=(datetime.datetime.now()))
        given_leaves[i] = AcceptDeclineDateForm(user_dates=dates).as_p()

    # Given shifts
    accepted_shifts = Request_shift.objects.filter(
        giver_shift_id__owner__username=request.user,
        accepted=True,
    ).values_list(
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'user_shift__owner__first_name',
        'user_shift__owner__last_name',
        'note',
    ).exclude(user_shift__date__lt=(datetime.datetime.now()))

    # Recover all the shifts the connected user can exchange
    request_shifts = Request_shift.objects.filter(
        giver_shift_id__owner__username=request.user,
        user_shift__date__gt=(datetime.datetime.now()),
        accepted=None,
    ).values_list(
        'user_shift',
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'note')

    shifts_forms = {}
    for item2 in request_shifts:
        shifts_forms[item2[0]] = AcceptDeclineForm(shift_id=item2[0]).as_p()

    context = {'gifts': gifts,
               'gifts_form': gifts_form,
               'accepted_leaves': accepted_leaves,
               'leaves': given_leaves,
               'request_leaves': request_leaves,
               'accepted_shifts': accepted_shifts,
               'request_shifts': request_shifts,
               'request_shifts_forms': shifts_forms}
    return render(request, 'inform/exchanges.html', context)


def validate(request):
    if request.method == 'POST':
        shift = request.POST['id']
        status = request.POST.get('status')
        if 'accept_decline_date' in request.POST:
            dates = request.POST['accept_decline_date']
            form = AcceptDeclineDateForm(request.POST, user_dates=dates)
        else:
            dates = None
            form = AcceptDeclineForm(request.POST, shift_id=shift)

        if form.is_valid():
            if dates:
                date_leave = form.cleaned_data['accept_decline_date']
            if status == 'Decline':
                match dates:
                    case str():
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user
                        ).update(accepted=False)
                    case None:
                        Request_shift.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user
                        ).update(accepted=False)
            elif status == 'Accept':
                match dates:
                    case 'À discuter':
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user,
                        ).update(accepted=True)
                    case str():
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user,
                        ).update(
                            accepted=True,
                            given_leave=date_leave,
                        )
                        Give_leave.objects.filter(
                            shift=date_leave
                        ).update(
                            given=True,
                            who=request.user)
                    case None:
                        Request_shift.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user,
                        ).update(accepted=True)
    else:
        if 'accept_decline_date' in request.POST:
            AcceptDeclineDateForm()
        else:
            AcceptDeclineForm()

    return HttpResponseRedirect(reverse('exchanges'))


def delete(request):
    if request.method == 'POST':
        shift = request.POST['leave']
        form = DeleteForm(request.POST, leave_id=shift)
        if form.is_valid():
            shift = form.cleaned_data['leave']
            Request_leave.objects.filter(
                giver_shift=shift,
                giver_shift__owner__username=request.user,
            ).update(validated=False)
            Give_leave.objects.filter(
                shift=shift,
                shift__owner__username=request.user
            ).delete()
    else:
        DeleteForm()

    return HttpResponseRedirect(reverse('exchanges'))


@login_required
def wishes(request):
    # Show leave accepted or to negotiate
    accepted_wishes = Request_leave.objects.filter(
        user_shift__owner__username=request.user,
        accepted=True,
    ).values_list(
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'giver_shift__owner__first_name',
        'giver_shift__owner__last_name',
        'given_leave__date',
        'note',
    ).exclude(user_shift__date__lt=datetime.datetime.now())
    # Show accepted shifts
    accepted_shifts = Request_shift.objects.filter(
        user_shift__owner__username=request.user,
        accepted=True,
    ).values_list(
        'user_shift__date',
        'giver_shift__start_hour',
        'giver_shift__end_hour',
        'giver_shift__owner__first_name',
        'giver_shift__owner__last_name',
        'note',
    ).exclude(user_shift__date__lt=datetime.datetime.now())
    # Show only one wish per date
    user_wishes = Request_leave.objects.filter(
        user_shift__owner__username=request.user,
        accepted=None,
    ).values_list(
        'user_shift',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'note',
    ).exclude(Q(
        user_shift__date__lt=datetime.datetime.now()
    ) | Q(accepted=True)
    ).distinct()
    wishes_dict = {}
    for item in user_wishes:
        wishes_dict[item[0]] = DeleteForm(leave_id=item[0]).as_p()

    # Wish to change the schedule
    schedules = Request_shift.objects.filter(
        user_shift__owner__username=request.user,
        accepted=None,
    ).values_list(
        'user_shift',
        'user_shift__date',
        'note',
        'request__start_hour1',
        'request__start_hour2',
        'request__end_hour1',
        'request__end_hour2',
    ).exclude(Q(
        user_shift__date__lt=datetime.datetime.now()
    ) | Q(accepted=True)
    ).distinct()
    schedules_form = {}
    for day in schedules:
        schedules_form[day[0]] = DeleteForm(leave_id=day[0])

    context = {'accepted_wishes': accepted_wishes,
               'accepted_shifts': accepted_shifts,
               'wishes': user_wishes,
               'wishes_form': wishes_dict,
               'schedules': schedules,
               'schedules_form': schedules_form}
    return render(request, 'inform/wishes.html', context)


def delete_wish(request):
    if request.method == 'POST':
        shift = request.POST['leave']
        form = DeleteForm(request.POST, leave_id=shift)
        if form.is_valid():
            shift = form.cleaned_data['leave']
            if 'shift' in request.POST:
                Request_shift.objects.filter(
                    user_shift=shift,
                    user_shift__owner__username=request.user,
                ).exclude(accepted=True).delete()
            else:
                Request_leave.objects.filter(
                    user_shift=shift,
                    user_shift__owner__username=request.user,
                ).exclude(accepted=True).delete()
    else:
        DeleteForm()

    return HttpResponseRedirect(reverse('wishes'))
