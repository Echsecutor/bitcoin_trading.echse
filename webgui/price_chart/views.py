from django.shortcuts import render

from .models import Transaction
from django.db.models import Max

import logging

from . import api_call

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html')


def chart(request):
    data = Transaction.objects.order_by('tid')
    context = {
        'data': [row for row in data],
    }
    return render(request, 'chart.html', context)


def data(request):
    # get new transactions from API if keys given
    if request.POST and request.POST['key'] and request.POST['sec']:
        logger.info("Retrieving new transactions from API.")
        api = api_call.BCdeSession(request.POST['key'], request.POST['sec'])
        max_tid_agg = Transaction.objects.all().aggregate(Max('tid'))
        max_tid = 0
        if max_tid_agg:
            max_tid = max_tid_agg['tid__max']
        logger.debug("Max tid = %s", max_tid)
        new_trades = api.get_public_trade_history(max_tid)
        logger.debug("Api returned %s", new_trades)

        for row in new_trades['trades']:
            insert = Transaction(
                tid=row['tid'],
                date=row['date'],
                price=row['price'],
                amount=row['amont'],
                trading_pair=new_trades['trading_pair']
            )
            insert.save()

    # reder all data in DB
    data = Transaction.objects.order_by('tid')
    context = {
        'data': data,
    }
    return render(request, 'data.html', context)
