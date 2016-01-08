# plot_example_6.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410

from __future__ import print_function
import numpy, putil.plot

def panel_iterator_example(no_print):
    source1 = putil.plot.BasicSource(
        indep_var=numpy.array([1, 2, 3, 4]),
        dep_var=numpy.array([1, -10, 10, 5])
    )
    source2 = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([50, 75, 100, 125])
    )
    series1 = putil.plot.Series(
        data_source=source1,
        label='Goals'
    )
    series2 = putil.plot.Series(
        data_source=source2,
        label='Saves',
        color='b',
        marker=None,
        interp='STRAIGHT',
        line_style='--'
    )
    panel = putil.plot.Panel(
        series=[series1, series2],
        primary_axis_label='Time',
        primary_axis_units='sec',
        display_indep_axis=True
    )
    if not no_print:
        for num, series in enumerate(panel):
            print('Series {0}:'.format(num+1))
            print(series)
            print('')
    else:
        return panel
