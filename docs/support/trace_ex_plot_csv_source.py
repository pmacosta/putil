# trace_ex_plot_csv_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace plot csv_source module exceptions """
    mname = 'csv_source'
    fname = 'plot'
    module_prefix = 'putil.plot.{0}.CsvSource.'.format(mname)
    callable_names = (
        '__init__',
        'file_name',
        'rfilter',
        'indep_col_label',
        'dep_col_label',
        'indep_min',
        'indep_max',
        'fproc',
        'fproc_eargs',
        'indep_var',
        'dep_var'
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print, ['putil.eng']
    )


if __name__ == '__main__':
    trace_module(False)
