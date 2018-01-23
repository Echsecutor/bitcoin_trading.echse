"""
some simple p_data anaylysis of bitcoin trades p_data

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
import logging
import datetime


def bin_dated_data(p_data,
                   p_date_index=0,
                   p_bin_width=datetime.timedelta(days=1)):
    """@pre: p_data is sorted by index p_date_index

    Return the list of indices of the bin borders.
    I.e. the bins are [bin_border[i]:bin_border[i+1]-1]
    where bin_border[0]=0 and bin_border[len(bin_border)-1] = len(p_data)

    @post: Within each bin, the maximal datetime difference is
    guaranteed to be <= p_bin_width.

    @post: p_data[bin_border[i+1]][p_date_index] - p_data[bin_border[i]][p_date_index] > p_bin_width

    """
    bin_border = [0, ]
    last_bin_at = 0
    i = 0
    # todo: speedup by using binary search
    while i < len(p_data):
        # assert sorted pre condition
        assert p_data[i][p_date_index] >= p_data[last_bin_at][p_date_index]

        if p_data[i][p_date_index] - p_data[last_bin_at][p_date_index] > p_bin_width:
            bin_border.append(i)
            last_bin_at = i
        i += 1
    bin_border.append(len(p_data))
    return bin_border


def get_percentiles(
        p_data,
        p_data_index=2,
        p_percentiles_at=None):
    """Return a list of len = len(p_percentiles_at) the percentiles.
    I.e. the minimum values such that the given ratio of the p_data
    points are <= than the respective values.  In particular, the
    percentiles 0, 0.5 and 1 correspond to the minimum, median and
    maximum values. (This is the default.)

    p_data should be something like
    db.get_trades_in_time_window(p_from, p_to, p_trading_pair)
    """
    if not p_percentiles_at:
        p_percentiles_at = [0, 0.5, 1]
    num = len(p_data)
    p_percentiles_at.sort()
    p_data.sort(key=lambda x: x[p_data_index])
    current_pos = 0
    percentile_at = int(p_percentiles_at[0] * num)
    percentiles = []
    for row in p_data:
        current_pos += 1
        while percentile_at <= current_pos:
            percentiles.append(row[p_data_index])
            if len(percentiles) < len(p_percentiles_at):
                percentile_at = int(p_percentiles_at[len(percentiles)] * num)
            else:
                percentile_at = num + 1
                break
            assert percentile_at <= num

    logging.debug("percentiles: %s\nfor data: %s\nare: %s",
                  p_percentiles_at, p_data, percentiles)
    assert len(percentiles) == len(p_percentiles_at)

    return percentiles
