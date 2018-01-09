"""
sqllite db module for bitcoin api

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
import sqlite3

__connection = None

__trades_table_name = "public_trade_history"


def init_connect_db(p_db_file_name):
    """
    Open/Create database and create schema, if necessary.
    Return connection.
    """
    global __connection
    global __trades_table_name

    __connection = sqlite3.connect(p_db_file_name)
    c = __connection.cursor()

    # Create table if not existing
    c.execute("CREATE TABLE IF NOT EXISTS "
              + __trades_table_name
              + "(date text, price real, amount real, tid INTEGER PRIMARY KEY)")
    __connection.commit()


def close():
    """Close the module level connection.
    """
    __connection.close()


def insert_trades(trades):
    """
    pre: __connection initialised
    Insert new trades into the DB.
    Expects list of dicts as returned by the api.
    """
    global __connection
    global __trades_table_name
    
    c = __connection.cursor()

    for trade in trades:
        trade_list = [__trades_table_name, trade["date"], trade["price"], trade["amount"], trade["tid"]]
        c.execute('INSERT INTO ? VALUES (?,?,?,?,?)', trade_list)
    __connection.commit()


def get_trades():
    """
    Retrieve all trades from the DB.
    pre: __connection initialised
    """
    global __connection
    global __trades_table_name

    c = __connection.cursor()

    return c.execute('SELECT * FROM ?', [__trades_table_name, ])
