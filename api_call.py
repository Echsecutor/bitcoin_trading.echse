"""
This module facilitates the details of the api connection.
See https://www.bitcoin.de/de/api/tapi/v2/docu

.. moduleauthor:: Sebastian Schmittner <sebastian@schmittner.pw>


Copyright 2017 Sebastian Schmittner

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

import hashlib
from http.client import HTTPConnection
import hmac
import logging
import requests
import time

c_private_key = ""
"API secret"

c_public_key = ""
"API key"

c_api_url = "https://api.bitcoin.de/v2"
"Base url for all calls"

__credits = 20


def generate_api_signature(method, url, nonce, post_params):
    """
    Generate and return X-API-SIGNATURE according to
    http://www.bitcoin.de/de/api/tapi/v2/docu
    """
    sorted_params = []
    for key, val in post_params.items():
        sorted_params.append("{}={}".format(key, val))
    sorted_params.sort()
    query_string = "?".join(sorted_params)
    logging.debug("query_string: '{}' = {}".format(query_string, query_string.encode()))
    hashed_query_string = hashlib.md5(query_string.encode()).hexdigest()
    hmac_data = "{}#{}#{}#{}#{}".format(
        method,
        url,
        c_public_key,
        nonce,
        hashed_query_string
        )
    logging.debug("hamc_data: %s", hmac_data)

    return hmac.new(
        c_private_key.encode(),
        msg=hmac_data.encode(),
        digestmod="sha256").hexdigest()


def query(url, method="GET", post_params={}, headers={}):
    """
    method should be "GET", "POST", etc.
    """
    global __credits

    if __credits < 3:
        logging.warning("Not enough credits (to high request frequency. Sleepingfor3seconds...")
        time.sleep(3)
    else:
        logging.debug("We have at least %s credits", __credits)

    headers['X-API-KEY'] = c_public_key
    headers['X-API-NONCE'] = str(int(time.time()))
    headers['X-API-SIGNATURE'] = generate_api_signature(
        method, url, headers['X-API-NONCE'], post_params)

    logging.debug("headers={}".format(headers))

    r = requests.get(url, headers=headers)
    logging.debug("Response %s = %s",
                  r.status_code,
                  r.reason)

    if r.status_code == 200:
        __credits = r.json()["credits"]

    return r


def get_public_trade_history(since_tid=None):
    """
    Query the btceur trade history and return the JSON answer.
    Return None on error.
    """
    url = c_api_url + "/trades/history?trading_pair=btceur"
    if since_tid:
        url += "&since_tid={}".format(since_tid)

    r = query(url)

    if r.status_code != 200:
        logger.error("Error getting trade history. Response %s", r.status_code)
        return None

    return r.json()
