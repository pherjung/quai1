from django.shortcuts import render
from django.template.defaulttags import register
import datetime
from exchange.models import Ask_leave, Give_leave
from .forms import AcceptDeclineForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


def exchanges(request):
    asker_ids = set()
    # Recover all the leave the connected user can exchange
    ask_leaves = Ask_leave.objects.filter(
        giver_shift_id__owner__username=request.user,
        user_shift__date__gt=(datetime.datetime.now())
    ).values_list(
        'user_shift__shift_name',
        'user_shift__date',
        'user_shift__start_hour',
        'user_shift__end_hour',
        'user_shift__owner',
        'user_shift__owner__username',
        'note',
        'gift')

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
            'shift__date',
            'shift__owner__username')
        given_leaves[i] = AcceptDeclineForm(dates)

    context = {'leaves': given_leaves,
               'ask_leaves': ask_leaves}
    return render(request, 'inform/exchanges.html', context)


def wishes(request):
    return render(request, 'inform/wishes.html')
