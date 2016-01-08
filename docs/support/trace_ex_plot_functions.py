# trace_ex_plot_functions.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace plot functions module exceptions """
    mname = 'functions'
    fname = 'plot'
    module_prefix = 'putil.plot.{0}.'.format(mname)
    callable_names = (
        'parameterized_color_space',
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, ['putil.eng']
    )


if __name__ == '__main__':
    trace_module(False)
