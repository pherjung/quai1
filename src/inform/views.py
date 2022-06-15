import json
from datetime import datetime
from django.template.defaulttags import register
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from exchange.models import Request_leave, Give_leave, Request_shift, Request_shift_log, Request_leave_log
from .forms import AcceptDeclineDateForm, DeleteForm, AcceptDeclineForm, ValidateForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def exchanges(request):
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
    requester_ids = set()
    leaves = 0
    while leaves < len(request_leaves):
        # Recover all requesters
        requester_ids.add(request_leaves[leaves][4:])
        leaves += 1

    given_leaves = {}
    for i in requester_ids:
        dates = Give_leave.objects.filter(
            shift__owner=i[1],
            given=False
        ).values_list(
            'shift',
            'shift__date'
        ).exclude(shift__date__lt=(datetime.now()))
        given_leaves[i[0]] = AcceptDeclineDateForm(user_dates=dates).as_p()

    context = {'request_leaves': request_leaves,
               'given_leaves': given_leaves}
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
                        # Nouveau formulaire avec plusieurs dates
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
                            given_shift=date_leave,
                        )
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
