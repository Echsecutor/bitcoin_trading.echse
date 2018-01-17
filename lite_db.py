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


TRADES_TABLE_NAME = "public_trade_history"
"const schema"


TRADES_TABLE_COMUMNS = [("trading_pair", "text"),
                          ("date", "text"),
                          ("price", "real"),
                          ("amount", "real"),
                          ("tid", "INTEGER PRIMARY KEY")]
"const schema"

TRADES_TABLE_COMUMNS_NAMES = "(" + ", ".join(x[0] for x in TRADES_TABLE_COMUMNS) + ")"
"const schema"


class DBCoin(object):
    def __init__(self, p_db_file_name):
        """
        Open/Create database and create schema, if necessary.
        Return connection.
        """
        self.connection = sqlite3.connect(p_db_file_name)
        # Create table if not existing
        create_query = "CREATE TABLE IF NOT EXISTS "
        create_query += TRADES_TABLE_NAME + "("
        create_query += ", ".join(column_name + " " + column_type for (column_name, column_type) in TRADES_TABLE_COMUMNS)
        create_query += ")"

        with self.connection:
            self.connection.execute(create_query)

    def close(self):
        """Close the module level connection.
        """
        self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def insert_trades(self, p_publi_trades_history_json):
        """
        pre: __connection initialised
        Insert new trades into the DB.
        Expects json with list of trades dicts and trading_pair
        as returned by the api.
        """
        trades = p_publi_trades_history_json["trades"]
        with self.connection:
            for trade in trades:
                trade_list = []

                for column_name in [x[0] for x in TRADES_TABLE_COMUMNS]:
                    if column_name in p_publi_trades_history_json:
                        trade_list.append(
                            p_publi_trades_history_json[column_name])
                    else:
                        trade_list.append(trade[column_name])

                self.connection.execute("INSERT OR IGNORE INTO "
                          + TRADES_TABLE_NAME
                          + TRADES_TABLE_COMUMNS_NAMES
                          + " VALUES (?,?,?,?,?)",
                          trade_list)

    def get_max_tid(self):
        with self.connection:
            return self.connection.execute("SELECT max(tid) FROM " + TRADES_TABLE_NAME).fetchone()[0]


    def get_trades_in_time_window(self, p_from, p_to, p_trading_pair="btceur"):
        """
        return all trades with from <= date < to
        """
        with self.connection:
            return [row for row in self.connection.execute('SELECT * FROM ' + TRADES_TABLE_NAME + ' WHERE (date >= ? AND date < ?', (p_from, p_to))]


    def get_all_trades(self):
        """
        Retrieve all trades from the DB.
        pre: __connection initialised
        """
        with self.connection:
            return [row for row in self.connection.execute('SELECT * FROM ' + TRADES_TABLE_NAME)]


    def get_num_trades(self):
        with self.connection:
            return self.connection.execute("SELECT COUNT(tid) from " + TRADES_TABLE_NAME).fetchone()[0]
