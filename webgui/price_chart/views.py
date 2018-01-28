from django.shortcuts import render
from django.db import transaction
from django.db.models import Max
from datetime import datetime, timezone, timedelta

from django.http import JsonResponse

import logging

from . import api_call, data_analysis
from .models import Transaction

logger = logging.getLogger(__name__)


def index(request):
    """This is the only full page view rendering all containers.
    Content is added by ajax requests.
    """
    return render(request, 'index.html')


def chart(request):
    db_data = [(x[0], x[1]) for x in Transaction.objects.order_by('tid').values_list("date", "price")]
    db_data.sort(key=lambda x: x[0])
    # todo: UI
    delta = timedelta(days=1)
    bins = data_analysis.bin_dated_data(db_data, 0, delta)
    percentiles_at = [0, 0.3, 0.5, 0.7, 1.0]
    percentiles = [
        data_analysis.get_percentiles(
            db_data[bins[i]:bins[i+1]-1],
            p_data_index=1,
            p_percentiles_at=percentiles_at)
        for i in range(0, len(bins)-1)
    ]
    chart_data = {
        "labels": [str(db_data[b][0]) for b in bins[:-2]],
        "datasets": [
            {
                "fill": "+1",
                "label": "p" + str(percentiles_at[i]),
                "data": [float(x[i]) for x in percentiles]
            }
            for i in range(0, len(percentiles_at))
            ]
    }
    chart_data["datasets"][-1]["fill"] = "0"

    return JsonResponse({
        'status': 200,
        "chart_data": chart_data
    })


def retrieve_data_from_api(request):
    "get new transactions from API, needs API key + secret"
    try:
        num_inserted = 0
        logger.info("Retrieving new transactions from API.")

        key, sec = request.POST['key'], request.POST['sec']
        if not key or not sec:
            return JsonResponse({
                'status': 400,
                'msg': "API key incomplete or missing."
            })

        api = api_call.BCdeSession(key, sec)
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
    # todo: more specific catches/error codes
    except Exception as ex:  #pylint: disable=W
        return JsonResponse({
            'status': 500,
            'msg': str(ex)
        })


def data(request):
    # reder all data in DB
    data_db = Transaction.objects.order_by('tid')
    data_list = [row for row in data_db]
    # do only show the last 100
    # 2 do: use a proper data table instead
    context = {
        'status': 200,
        'data': data_list[-100:],
        'num_total': len(data_list)
    }
    return render(request, "data_table.html", context)
