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
from http.client import HTTPConnection
import logging

import api_call
import lite_db

def read_key_from_file(filename):
    "Read and return first line of a file"
    with open(filename, "r") as key_file:
        return key_file.readline()


def update_trades():
    """
    pre: set the public and private key for the api_call module.
    pre: initialise lite_dbconnection
    """
    logging.info("Updating trades DB...")

    max_tid = lite_db.get_max_tid()
    r = api_call.get_public_trade_history(max_tid)
    if not r:
        logging.error("Could not retrieve trade history")
        return
    lite_db.insert_trades(r)


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
    parser.add_argument(
        "-d",
        "--database-file",
        help="Name of the sqllite db file to use",
        default="bitcoin.db")

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

    api_call.c_private_key = read_key_from_file(args.secret)[:-1]
    api_call.c_public_key = read_key_from_file(args.key)[:-1]

    logging.debug("public key: %s", api_call.c_public_key)

    lite_db.init_connect_db(args.database_file)

    update_trades()

    logging.debug("%s trades in DB", lite_db.get_num_trades())

    lite_db.close()
    logging.info("[FINISHED]")


# goto main
if __name__ == "__main__":
    main()
