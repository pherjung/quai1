import json
from datetime import datetime
from django.template.defaulttags import register
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from exchange.models import Request_leave, Request_leave_log, Give_leave, Request_shift, Request_shift_log
from exchange import rest_time
from calendrier.models import Shift
from .forms import AcceptDeclineDateForm, AcceptDeclineForm, DeleteForm, ValidateForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def gifts(request):
    date = datetime.strptime(json.loads(request.body), '%A %d %B %Y')
    gifts = Give_leave.objects.filter(
        shift__owner__username=request.user,
        shift__date=date,
        given=False,
    ).values_list(
        'shift',
        'shift__date',
    ).exclude(shift__date__lt=(datetime.now()))
    gifts_form = {}
    for item in gifts:
        gifts_form[item[0]] = DeleteForm(leave_id=item[0])

    context = {'gifts': gifts,
               'gifts_form': gifts_form}
    return render(request, 'inform/gifts.html', context)

def wishes(request):
    date = datetime.strptime(json.loads(request.body), '%A %d %B %Y')
    user_wishes = Request_leave_log.objects.filter(
        user=request.user,
        active=True,
        date=date,
    ).values_list(
        'id',
        'date',
        'note')

    context = {'wishes': user_wishes}
    return render(request, 'inform/user_wishes.html', context)


def delete_wish(request):
    if request.method == 'POST':
        shift = request.POST['leave']
        form = DeleteForm(request.POST, leave_id=shift)
        if form.is_valid():
            Give_leave.objects.filter(
                shift=shift,
                shift__owner__username=request.user
            ).delete()
    else:
        DeleteForm()

    return HttpResponseRedirect(reverse('calendar'))


def retrieve_ungiven_leaves(request):
    date = datetime.strptime(json.loads(request.body), '%A %d %B %Y')
    # Recover all the leave the connected user can exchange
    request_leaves = Request_leave.objects.filter(
        giver_shift__date=date,
        giver_shift_id__owner__username=request.user,
        user_shift__date__gt=(datetime.now()),
        accepted=None,
    ).values_list(
        'user_shift__shift_name',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'note',
        'user_shift',
        'user_shift__owner')
    # Recover all requesters
    requester_ids = [users[4:] for users in request_leaves]
    keeped_date = {}
    for users in request_leaves:
        keeped_date[users[5]] = []
    # Recover all leaves requesters give
    given_leaves = {}
    # Do not propose a leave if the donor already has one
    dates = Give_leave.objects.filter(
        shift__owner__in=[uids[1] for uids in requester_ids],
        given=False
    ).values_list('shift', 'shift__date',
                  'shift__owner__username', 'shift__owner',
                  ).exclude(shift__date__lt=datetime.now())
    for day in dates:
        try:
            user_leave = Shift.objects.get(owner=request.user, date=day[1])
            if user_leave.shift_name == '200' or user_leave.start_hour:
                # Check if donor can swap his shift
                rest = rest_time.start_end_hour(day[1], day[2])
                if user_leave.start_hour and user_leave.start_hour < rest['start_hour']:
                    continue
                if user_leave.end_hour and user_leave.end_hour > rest['end_hour']:
                    continue
                keeped_date[day[3]].append(day[1])
        except Shift.DoesNotExist:
            keeped_date.append(day[1])

    for i in requester_ids:
        given_leaves[i[0]] = AcceptDeclineDateForm(
            user_dates=dates.filter(shift__date__in=keeped_date[i[1]],
                                    shift__owner=i[1])).as_p()
    return request_leaves, given_leaves


def recover_ungiven_shift(request):
    """
    Recover all the shifts the connected user can exchange
    """
    request_shifts = Request_shift.objects.filter(
        giver_shift_id__owner__username=request.user,
        user_shift__date__gt=(datetime.now()),
        accepted=None,
    ).values_list(
        'user_shift__shift_name',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'note',
        'user_shift')
    shifts_forms = {}
    for item2 in request_shifts:
        shifts_forms[item2[4]] = AcceptDeclineForm(shift_id=item2[0]).as_p()

    return request_shifts, shifts_forms


@register.filter
def exchanges(request):
    request_leaves, given_leaves = retrieve_ungiven_leaves(request)
    request_shifts, shifts_forms = recover_ungiven_shift(request)
    context = {'request_leaves': request_leaves,
               'given_leaves': given_leaves,
               'request_shifts': request_shifts,
               'request_shifts_forms': shifts_forms}
    return render(request, 'inform/exchanges.html', context)


def validate(request):
    """
    Accept or decline leaves or shifts
    """
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
                    # Decline leave
                    case str():
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user
                        ).update(accepted=False)
                    # Decline shift
                    case None:
                        Request_shift.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user
                        ).update(accepted=False)
            elif status == 'Accept':
                match dates:
                    case 'À discuter':
                        # Nouveau formulaire avec plusieurs dates
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user,
                        ).update(accepted=True)
                    # Date is choosen -> accept leave
                    case str():
                        Request_leave.objects.filter(
                            user_shift=shift,
                            giver_shift__owner__username=request.user,
                        ).update(
                            accepted=True,
                            given_shift=date_leave,
                        )
                    # No date provided, as it is a shift swap
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

    return HttpResponseRedirect(reverse('calendar'))


def to_accept_leave(request):
    """Show accepted leaves"""
    date = datetime.strptime(json.loads(request.body), '%A %d %B %Y')
    accepted_leaves = Request_leave.objects.filter(
        user_shift__owner__username=request.user,
        user_shift__date=date,
        accepted=True,
        validated=False,
    ).values_list(
        'user_shift__date',
        'giver_shift__owner__first_name',
        'giver_shift__owner__last_name',
        'given_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'id',
        'giver_shift__owner__email'
    ).exclude(user_shift__date__lt=datetime.now())
    leave_forms = {}
    for leave in accepted_leaves:
        leave_forms[leave[6]] = ValidateForm(request_leave=leave[6],
                                             exchange=leave[3])
    context = {'accepted_leaves': accepted_leaves,
               'leave_forms': leave_forms}
    return render(request, 'inform/wishes.html', context)


def confirm_leave(request):
    if request.method == 'POST':
        validate_data = request.POST['request_leave']
        exchange = request.POST['exchange']
        form = ValidateForm(request.POST,
                            request_leave=validate_data,
                            exchange=exchange)
        if form.is_valid():
            validate_data = form.cleaned_data['request_leave']
            exchanged_date = form.cleaned_data['exchange']
            shift = Shift.objects.get(date=exchanged_date,
                                      owner__username=request.user)
            request_leave = Request_leave.objects.get(id=validate_data)
            Give_leave.objects.update_or_create(
                shift=shift,
                defaults={'given': True,
                          'who': request_leave.giver_shift.owner},
            )
            Request_leave.objects.filter(
                id=validate_data
            ).update(validated=True, given_shift=shift)
            Request_leave.objects.filter(
                Q(user_shift__owner__username=request.user)
                | Q(giver_shift__owner=request_leave.giver_shift.owner),
                user_shift__date=request_leave.user_shift.date,
            ).exclude(id=validate_data).delete()
            Request_leave_log.objects.filter(
                user=request.user,
                id=request_leave.request.id,
            ).update(active=False)
        else:
            print("You have to give back a leave")
    return HttpResponseRedirect(reverse('calendar'))


def to_accept_shift(request):
    """Show accepted shifts"""
    date = datetime.strptime(json.loads(request.body), '%A %d %B %Y')
    # Show accepted shifts
    accepted_shifts = Request_shift.objects.filter(
        user_shift__owner__username=request.user,
        user_shift__date=date,
        accepted=True,
        confirmed=False,
    ).values_list(
        'user_shift__date',
        'giver_shift__owner__first_name',
        'giver_shift__owner__last_name',
        'giver_shift__start_hour',
        'giver_shift__end_hour',
        'user_shift',
        'giver_shift',
        'request',
        'giver_shift__owner__email',
    ).exclude(user_shift__date__lt=datetime.now())
    shift_forms = {}
    for switch in accepted_shifts:
        shift_forms[switch[7]] = ValidateForm(request_leave=switch[5],
                                              exchange=switch[6])
    context = {'accepted_shifts': accepted_shifts,
               'shift_forms': shift_forms}
    return render(request, 'inform/wishes.html', context)


def confirm_shift(request):
    if request.method == 'POST':
        validate_data = request.POST['request_leave']
        exchange = request.POST['exchange']
        form = ValidateForm(request.POST,
                            request_leave=validate_data,
                            exchange=exchange)
        if form.is_valid():
            request_shift = Request_shift.objects.filter(
                user_shift=form.cleaned_data['request_leave'],
                giver_shift=form.cleaned_data['exchange'],
            ).values('request')
            request_shift.update(confirmed=True)
            Request_shift.objects.filter(
                user_shift=form.cleaned_data['request_leave'],
            ).exclude(
                giver_shift=form.cleaned_data['exchange'],
            ).delete()
            Request_shift_log.objects.filter(
                id=request_shift[0]['request'],
            ).update(active=False)

    return HttpResponseRedirect(reverse('calendar'))
