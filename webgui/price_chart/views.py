"""
.. moduleauthor:: Sebastian Schmittner <sebastian@schmittner.pw> and Jan Schmidt


Copyright 2017-2018 Sebastian Schmittner

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

from django.shortcuts import render
from datetime import timedelta

from django.http import JsonResponse

import logging

from . import data_analysis, etl, models

logger = logging.getLogger(__name__)


def index(request):
    """This is the only full page view rendering all containers.
    Content is added by ajax requests.
    """
    return render(request, 'index.html')


# request is not used on purpose. ;)
def chart(request):#pylint: disable=W
    # todo: UI -> choose pair
    curIn = request.POST.get("curIn", "btc")
    curOut = request.POST.get("curOut", "eur")

    db_data = [
        (x[0], x[1])
        for x in models.Trade.objects.filter(
                curIn=curIn, curOut=curOut).order_by(
                    'date').values_list("date", "rate")
    ]

    if not db_data:
        return JsonResponse({
            'status': 200,
            "chart_data": {},
            "msg": "No data in DB"
        })

    # todo: UI->choose bins
    days = int(request.POST.get("days", "1"))
    hours = int(request.POST.get("hours", "0"))
    delta = timedelta(days=days, hours=hours)
    bins = data_analysis.bin_dated_data(db_data, 0, delta)

    # todo: UI -> choose percentiles
    percentiles_at = [0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    percentiles = [
        data_analysis.get_percentiles(
            db_data[bins[i]:bins[i+1]-1],
            p_data_index=1,
            p_percentiles_at=percentiles_at)
        for i in range(0, len(bins)-1)
    ]
    chart_data = {
        "labels": [str(db_data[b][0]) for b in bins[:-1]],
        "datasets": [
            {
                "fill": "+1",
                "borderColor": "rgb(" + str(i * 23 % 256) + "," + str((i + 1) * 7727 % 256) + "," + str(i * 67 % 256) + ")",
                "label": "p" + str(percentiles_at[i]),
                "data": [float(x[i]) for x in percentiles]
            }
            for i in range(0, len(percentiles_at))
            ]
    }
    for ds in chart_data["datasets"]:
        ds["backgroundColor"] = ds["borderColor"]
    chart_data["datasets"][-1]["fill"] = "0"

    return JsonResponse({
        'status': 200,
        "chart_data": chart_data
    })


def retrieve_data_from_api(request):
    "get new transactions from APIs, needs API key + secret for bitcoin.de"
    try:
        logger.info("Retrieving new transactions from API.")

        key = request.POST.get("key", None)
        sec = request.POST.get("sec", None)

        if not key or not sec:
            return JsonResponse({
                'status': 400,
                'msg': "API key incomplete or missing."
            })

        num_inserted = etl.from_bitcoin_de(key, sec)

        num_inserted += etl.from_shapeshift()

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
    # todo: UI how many?
    num = int(request.POST.get("num", "100"))
    total = models.Trade.objects.count()
    data_db = models.Trade.objects.order_by("-date")[:num]

    # todo: UI: use a proper data table instead
    context = {
        'status': 200,
        'data': data_db,
        'num_total': total
    }
    return render(request, "data_table.html", context)
