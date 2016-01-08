# plot_example_4.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410

import numpy, putil.plot

def create_basic_source():
    obj = putil.plot.BasicSource(
        indep_var=numpy.array([1, 2, 3, 4]),
        dep_var=numpy.array([1, -10, 10, 5]),
        indep_min=2, indep_max=3
    )
    return obj
