"""
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
from . import data_analysis
import datetime
import random
import itertools


def test_get_percentiles():
    "calculate and check some trivial percentiles"
    data = [
        [1],
        [2],
        [3],
        [4],
        [5],
        [6],
        [7],
        [8],
        [9],
        [10]
    ]
    data_index = 0

    # default percentiles
    percentiles_at = [0, 0.2, 0.4, 0.5, 0.6, 0.8, 1]
    percentiles = data_analysis.get_percentiles(data,
                                                data_index,
                                                percentiles_at)
    assert percentiles == [1, 2, 4, 5, 6, 8, 10]

    # not including 0/1
    percentiles_at = [0.3, 0.4, 0.8]
    percentiles = data_analysis.get_percentiles(data,
                                                data_index,
                                                percentiles_at)
    assert percentiles == [3, 4, 8]

    # only median
    percentiles_at = [0.5]
    percentiles = data_analysis.get_percentiles(data,
                                                data_index,
                                                percentiles_at)
    assert percentiles == [5]

    # multiple percentiles at same vaue
    percentiles_at = [.5, .55, .599999999, .6, .600000001]
    percentiles = data_analysis.get_percentiles(data,
                                                data_index,
                                                percentiles_at)
    assert percentiles == [5, 5, 5, 6, 6]


def test_bin_dated_data():
    """
    Generate some random dated data and bin it.
    """
    data = [
        (datetime.datetime(*dt), random.random())
        for dt in itertools.product(
                (2018, ),
                (1, 2),
                range(1, 25),
                range(0, 23),
                range(0, 59, 3),
                range(0, 59, 7))
    ]

    data.sort(key=lambda x: x[0])
    delta = datetime.timedelta(days=1)
    bins = data_analysis.bin_dated_data(data, 0, delta)

    assert bins[0] == 0
    assert bins[-1] == len(data)

    for i in range(0, len(bins) - 1):
        assert abs(data[bins[i]][0] - data[bins[i+1]-1][0]) <= delta
        if i > 0:
            assert abs(data[bins[i-1]][0] - data[bins[i]][0]) > delta
