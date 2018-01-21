from django.shortcuts import render
from django.db import transaction
from django.db.models import Max
from datetime import datetime, timezone

from django.http import JsonResponse

import logging

from . import api_call
from .models import Transaction

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html')


def chart(request):
    data = Transaction.objects.order_by('tid').values_list("date", "price")
    context = {
            'labels': [str(x[0]) for x in data],
            'data': [str(x[1]) for x in data]
            }
    return render(request, 'chart.html', context)


def retrieve_data_from_api(request):
    "get new transactions from API, needs API key + secret"
    try:
        num_inserted = 0
        logger.info("Retrieving new transactions from API.")
        api = api_call.BCdeSession(request.POST['key'], request.POST['sec'])
        max_tid = 0
        max_tid_agg = Transaction.objects.all().aggregate(Max('tid'))
        if max_tid_agg:
            max_tid = max_tid_agg['tid__max']
        logger.debug("Max tid = %s", max_tid)
        new_trades = api.get_public_trade_history(max_tid)
        logger.debug("Api returned %s", new_trades)

        if new_trades:
            # transaction for performance
            with transaction.atomic():
                for row in new_trades['trades']:
                    timestamp = datetime.fromtimestamp(float(row['date']))
                    insert = Transaction(
                        tid=row['tid'],
                        date=timestamp.replace(tzinfo=timezone.utc),
                        price=row['price'],
                        amount=row['amount'],
                        trading_pair=new_trades['trading_pair']
                    )
                    insert.save()
                    num_inserted += 1

        return JsonResponse({
            'status': 200,
            'inserted': num_inserted
        })
    except Exception as ex:
        return JsonResponse({
            'status': 500,
            'msg': str(ex)
        })


def data(request):
    # reder all data in DB
    data = Transaction.objects.order_by('tid')
    data_list = [row for row in data]
    # do only show the last 100
    # 2 do: use a proper data table instead
    context = {
        'data': data_list[-100:],
        'num_total': len(data_list)
    }
    return render(request, 'data.html', context)
