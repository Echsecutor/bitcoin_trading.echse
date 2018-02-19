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
    source = "bitcoin.de"
    api = apis.BCdeSession(key, sec)
    max_tid = 0
    max_tid_agg = models.Trade.objects.filter(source=source).aggregate(Max('source_id'))
    if max_tid_agg:
        max_tid = max_tid_agg['tid__max']
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
                    source=source,
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
