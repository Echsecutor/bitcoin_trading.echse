"""
Extract transaction data from apis, transform, and load into internal db.

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

from django.db import transaction
from django.db.models import Max

from datetime import datetime, timezone
import logging

from . import apis, models

logger = logging.getLogger(__name__)


def from_bitcoin_de(key, sec, curIn="btc", curOut="eur"):
    """
    Get latest trades on bitcoin.de.
    This API needs a priv/pub API key pair in order to connect.
    Return number of inserted rows.
    """
    api = apis.BCdeSession(key, sec)
    rows=models.Trade.objects.filter(source=api.name)
    max_tid = 0
    if rows.count() > 0:
        max_tid = rows.aggregate(Max('source_id'))['source_id__max']
    logger.debug("Max tid = %s", max_tid)
    new_trades = api.get_public_trade_history(max_tid, curIn + curOut)
    logger.debug("Api returned %s", new_trades)

    num_inserted = 0

    if new_trades:
        # transaction for performance
        with transaction.atomic():
            for row in new_trades['trades']:
                timestamp = datetime.fromtimestamp(float(row['date']))
                insert = models.Trade(
                    source=api.name,
                    source_id=row['tid'],
                    curIn=new_trades['trading_pair'][:3],
                    curOut=new_trades['trading_pair'][-3:],
                    date=timestamp.replace(tzinfo=timezone.utc),
                    rate=row['price'],
                    amount=row['amount']
                )
                insert.save()
                num_inserted += 1

    return num_inserted


def from_shapeshift():
    """
    Get latest trades from shapeshift.
    todo: Only gets 50 trades, hence this is not very useful.
    Return number of inserted rows.
    """
    api = apis.Shapeshift()
    recent_tx = api.recent_tx()
    num_inserted = 0
    for trade in recent_tx:
        info = api.get_marketinfo(trade["curIn"], trade["curOut"])
        timestamp = datetime.fromtimestamp(float(trade["timestamp"]))
        insert = models.Trade(
            source=api.name,
            source_id=trade["txid"],
            curIn=trade["curIn"],
            curOut=trade["curOut"],
            date=timestamp.replace(tzinfo=timezone.utc),
            rate=info["rate"],
            amount=trade['amount']
        )
        insert.save()
        num_inserted += 1

    return num_inserted
