# trace_ex_plot_figure.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace plot figure module exceptions """
    mname = 'figure'
    fname = 'plot'
    module_prefix = 'putil.plot.{0}.Figure.'.format(mname)
    callable_names = (
        '__init__',
        'show',
        'save',
        'indep_var_label',
        'indep_var_units',
        'title',
        'log_indep_axis',
        'fig_width',
        'fig_height',
        'panels',
        'fig',
        'axes_list'
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, ['putil.eng']
    )


if __name__ == '__main__':
    trace_module(False)
