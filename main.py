#!/usr/bin/python3
"""
This is a small python tool usign the bitcoin.de trading API v2.
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
import argparse
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

def read_key_from_file(filename):
    "Read and return first line of a file"
    with open(filename, "r") as key_file:
        return key_file.readline()

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


def get_public_trade_history(since_tid=None):
    url = c_api_url + "/trades/history?trading_pair=btceur"
    if since_tid:
        url += "&since_tid={}".format(since_tid)
    headers = {'X-API-KEY': c_public_key,
               'X-API-NONCE': str(int(time.time()))}

    headers['X-API-SIGNATURE'] = generate_api_signature(
        "GET", url, headers['X-API-NONCE'], {})
    logging.debug("headers={}".format(headers))

    r = requests.get(url, headers=headers)

    logging.debug("Response (%s = %s): %s",
                  r.status_code,
                  r.reason,
                  r.content)

    return r


def main():
    """The main function gets a list of all mailing lists on the given
    server and performs (an) action(s) on all lists.

    """
    global c_private_key
    global c_public_key

    logger_cfg = {
        "level":
        logging.INFO,
        "format":
        "%(asctime)s %(funcName)s (%(lineno)d) [%(levelname)s]:    %(message)s"
    }

    parser = argparse.ArgumentParser(
        description="Communicate with bitcoin.de using the trading API.\n" +
        "You need API keys!")
    parser.add_argument(
        "-k",
        "--key",
        required=True,
        help="The public key file.")
    parser.add_argument(
        "-s",
        "--secret",
        required=True,
        help="The private key file.")
    parser.add_argument(
        "-l",
        "--log",
        help="Set the log level. Default: INFO.",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO")

    args = parser.parse_args()

    logger_cfg["level"] = getattr(logging, args.log)
    logging.basicConfig(**logger_cfg)

    # in debug mode: full log all requests
    if logger_cfg["level"] <= 10:
        HTTPConnection.debuglevel = 1
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    print("Log messages above level: {}".format(logger_cfg["level"]))

    c_private_key = read_key_from_file(args.secret)[:-1]
    c_public_key = read_key_from_file(args.key)[:-1]

    logging.debug("public key: %s", c_public_key)

    get_public_trade_history()

    logging.info("[FINISHED]")


# goto main
if __name__ == "__main__":
    main()
