from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.template.defaulttags import register
import datetime
from exchange.models import Ask_leave, Give_leave
from .forms import AcceptDeclineForm, DeleteGiftedLeaveForm


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
    gifts_form = dict()
    for item in gifts:
        gifts_form[item[0]] = DeleteGiftedLeaveForm(leave_id=item[0])

    # Given leaves
    accepted = Ask_leave.objects.filter(
        giver_shift_id__owner__username=request.user,
        accepted=True
    ).values_list(
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'user_shift__owner__first_name',
        'user_shift__owner__last_name',
        'note',
    ).exclude(user_shift__date__lt=(datetime.datetime.now()))

    # Requested leaves
    asker_ids = set()
    # Recover all the leave the connected user can exchange
    ask_leaves = Ask_leave.objects.filter(
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
        'gift',
        'user_shift')

    leaves = 0
    while leaves < len(ask_leaves):
        # Recover all askers
        asker_ids.add(ask_leaves[leaves][4])
        leaves += 1

    given_leaves = dict()
    for i in asker_ids:
        dates = Give_leave.objects.filter(
            shift__owner=i,
            given=False
        ).values_list(
            'shift',
            'shift__date'
        ).exclude(shift__date__lt=(datetime.datetime.now()))
        given_leaves[i] = AcceptDeclineForm(user_dates=dates)

    context = {'gifts': gifts,
               'gifts_form': gifts_form,
               'accepted': accepted,
               'leaves': given_leaves,
               'ask_leaves': ask_leaves}
    return render(request, 'inform/exchanges.html', context)


def validate(request):
    if request.method == 'POST':
        dates = request.POST['accept_decline']
        shift = request.POST['id']
        status = request.POST.get('status')
        form = AcceptDeclineForm(request.POST, user_dates=dates)
        if form.is_valid():
            date_leave = form.cleaned_data['accept_decline']
            if status == 'Decline':
                Ask_leave.objects.filter(
                    user_shift=shift,
                    giver_shift__owner__username=request.user
                ).update(accepted=False)
            elif status == 'Accept':
                Ask_leave.objects.filter(
                    user_shift=shift,
                    giver_shift__owner__username=request.user
                ).update(accepted=True)
                if date_leave != 'À discuter':
                    Give_leave.objects.filter(
                        shift=date_leave
                    ).update(given=True)
    else:
        AcceptDeclineForm()

    return HttpResponseRedirect(reverse('exchanges'))


def delete(request):
    if request.method == 'POST':
        shift = request.POST['leave']
        form = DeleteGiftedLeaveForm(request.POST, leave_id=shift)
        if form.is_valid():
            shift = form.cleaned_data['leave']
            Ask_leave.objects.filter(
                giver_shift=shift,
                giver_shift__owner__username=request.user,
            ).update(gift=False)
            Give_leave.objects.filter(
                shift=shift,
                shift__owner__username=request.user
            ).delete()
    else:
        DeleteGiftedLeaveForm()

    return HttpResponseRedirect(reverse('exchanges'))


def wishes(request):
    return render(request, 'inform/wishes.html')
