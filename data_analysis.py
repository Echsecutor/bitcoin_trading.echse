"""
some simple data anaylysis of bitcoin trades data

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
import lite_db


def get_percentiles_for_time_window(p_from, p_to, p_percentiles=[0,0.2, 0.4, 0.5,0.6,0.8,1], p_trading_pair="btceur", p_data_index=2):
    """Return a list of len = len(p_percentiles) the percentiles.
    I.e. the minimum values such that the given ratio of the data
    points are <= than the respective values.  In particular, the
    percentiles 0, 0.5 and 1 correspond to the minimum, median and
    maximum values.
    """
    data = lite_db.get_trades_in_time_window(p_form,p_to, p_trading_pair)
    num = len(data)
    data.sort(key=lambda x: x[p_data_index])
    current_pos = 0
    percentile_at = int(p_percentiles[0] * num)
    percentiles = []
    for row in data:
        if percentile_at <= current_pos:
            percentiles.append(row[p_data_index])
            percentile_at = int(p_percentiles[0] * num)
            assert (percentile_at <= num)
        current_pos += 1

    assert(len(percentiles) == len(p_percentiles))

    return percentiles
