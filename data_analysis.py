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


def get_percentiles_for_time_window(p_from, p_to, p_percentiles=0.2, p_trading_pair="btceur", p_data_index=2):
    """Return the median and a numpy array of length
    floor(1/p_percentiles) + 1 containing the percentiles.  I.e. the
    minimum values such that 1, p_percentiles * total, 2 *
    p_percentiles * total, ..., all points are <= than the respective
    values.
    """
    data = lite_db.get_trades_in_time_window(p_form,p_to, p_trading_pair)
    num = len(data)
    data.sort(key=lambda x: x[p_data_index])
    current_pos = 0
    percentile_at = 0
    percentiles = []
    median = 0
    for row in data:
        if percentile_at <= current_pos:
            percentiles.append(row[p_data_index])
            percentile_at = min(num, percentile_at + p_percentiles * num)
        if current_pos == int(num / 2.):
            median = row[p_data_index]
        current_pos += 1

    assert(len(percentiles) == int(1. / p_percentiles) + 1)
    return median, percentiles
