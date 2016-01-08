# trace_ex_plot_csv_source.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
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
    module_exclude_list = ['putil.eng']
    callable_exclude_list = [
        'putil.pcsv.csv_file.CsvFile._set_cfilter',
        'putil.pcsv.csv_file.CsvFile._set_dfilter',
        'putil.pcsv.csv_file.CsvFile._set_has_header',
        'putil.pcsv.csv_file.CsvFile._validate_frow',
        'putil.pcsv.csv_file.CsvFile.data',
        'putil.pcsv.csv_file.CsvFile.header',
        'putil.pcsv.csv_file.CsvFile.cfilter',
        'putil.pcsv.csv_file.CsvFile.dfilter',
        'putil.pcsv.csv_file.CsvFile.reset_dfilter'
    ]
    return docs.support.trace_support.run_trace(
        mname,
        fname,
        module_prefix,
        callable_names,
        no_print,
        module_exclude_list,
        callable_exclude_list
    )


if __name__ == '__main__':
    trace_module(False)
