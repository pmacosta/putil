# plot_example_2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903

import putil.plot

class MySource(putil.plot.DataSource, object):
    def __init__(self):
        super(MySource, self).__init__()

    def __str__(self):
        return super(MySource, self).__str__()

    def _set_dep_var(self, dep_var):
        super(MySource, self)._set_dep_var(dep_var)

    def _set_indep_var(self, indep_var):
        super(MySource, self)._set_indep_var(indep_var)

    dep_var = property(
        putil.plot.DataSource._get_dep_var, _set_dep_var
    )

    indep_var = property(
        putil.plot.DataSource._get_indep_var, _set_indep_var
    )
