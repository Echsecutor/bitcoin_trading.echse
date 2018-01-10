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
"""Module level variable holding the sql lite db connection"""

__trades_table_name = "public_trade_history"
"const schema"

__trades_table_columns = [("trading_pair", "text"),
                          ("date", "text"),
                          ("price", "real"),
                          ("amount", "real"),
                          ("tid", "INTEGER PRIMARY KEY")]
"const schema"

__trades_table_columns_names = "(" + ", ".join(x[0] for x in __trades_table_columns) + ")"
"const schema"


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
    create_query = "CREATE TABLE IF NOT EXISTS "
    create_query += __trades_table_name + "("
    create_query += ", ".join(column_name + " " + column_type for (column_name, column_type) in __trades_table_columns)
    create_query += ")"

    c.execute(create_query)
    __connection.commit()


def close():
    """Close the module level connection.
    """
    __connection.close()


def insert_trades(publi_trades_history_json):
    """
    pre: __connection initialised
    Insert new trades into the DB.
    Expects json with list of trades dicts and trading_pair
    as returned by the api.
    """
    global __connection
    global __trades_table_name

    trades = publi_trades_history_json["trades"]
    c = __connection.cursor()

    for trade in trades:
        trade_list = []

        for column_name in [x[0] for x in __trades_table_columns]:
            if column_name in publi_trades_history_json:
                trade_list.append(
                    publi_trades_history_json[column_name])
            else:
                trade_list.append(trade[column_name])

        c.execute("INSERT OR IGNORE INTO "
                  + __trades_table_name
                  + __trades_table_columns_names
                  + " VALUES (?,?,?,?,?)",
                  trade_list)
    __connection.commit()


def get_max_tid():
    global __connection
    c = __connection.cursor()

    return c.execute("SELECT max(tid) FROM " + __trades_table_name).fetchone()[0]


def get_trades():
    """
    Retrieve all trades from the DB.
    pre: __connection initialised
    """
    global __connection
    global __trades_table_name

    c = __connection.cursor()

    return [row for row in c.execute('SELECT * FROM ' + __trades_table_name)]


def get_num_trades():
    c = __connection.cursor()
    return c.execute("SELECT COUNT(tid) from " + __trades_table_name).fetchone()[0]
