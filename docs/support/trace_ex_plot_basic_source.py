# trace_ex_plot_basic_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace plot basic_source module exceptions """
    mname = 'basic_source'
    fname = 'plot'
    module_prefix = 'putil.plot.{0}.BasicSource.'.format(mname)
    callable_names = (
        '__init__',
        'indep_min',
        'indep_max',
        'indep_var',
        'dep_var'
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, ['putil.eng']
    )


if __name__ == '__main__':
    trace_module(False)
