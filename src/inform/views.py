import json
from datetime import datetime
from django.template.defaulttags import register
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from exchange.models import Request_leave, Give_leave, Request_shift
from calendrier.models import Shift
from .forms import AcceptDeclineDateForm, AcceptDeclineForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


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
    # Recover all leaves requesters give
    given_leaves = {}
    # Do not propose a leave if the donor already has one
    dates = Give_leave.objects.filter(
        shift__owner__in=[uids[1] for uids in requester_ids],
        given=False
    ).values_list('shift', 'shift__date'
                  ).exclude(shift__date__lt=datetime.now())
    try:
        has_user_leave = Shift.objects.get(owner=request.user, date=date)
        if has_user_leave.shift_name == '200' or has_user_leave.start_hour:
            keeped_date = date
        else:
            keeped_date = None
    except Shift.DoesNotExist:
        keeped_date = date

    for i in requester_ids:
        given_leaves[i[0]] = AcceptDeclineDateForm(
            user_dates=dates.filter(shift__date=keeped_date,
                                    shift__owner=i[1])).as_p()
    return request_leaves, given_leaves


@register.filter
def exchanges(request):
    request_leaves, given_leaves = retrieve_ungiven_leaves(request)
    context = {'request_leaves': request_leaves,
               'given_leaves': given_leaves}
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
