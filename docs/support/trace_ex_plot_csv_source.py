# trace_ex_plot_csv_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

from __future__ import print_function
import copy, datetime, os, pytest

import putil.exdoc, putil.misc


def trace_module(no_print=True):
    """ Trace plot module exceptions """
    noption = os.environ.get('NOPTION', None)
    start_time = datetime.datetime.now()
    pickle_file_name = os.path.join(
        os.path.dirname(__file__),
        'csv_source.pkl'
    )
    with putil.exdoc.ExDocCxt(
            exclude=['_pytest', 'execnet', 'putil.eng'],
            file_name=pickle_file_name
    ) as exdoc_obj:
        if pytest.main('-x {0}-k TestCsvSource {1}'.format(
                '{0} '.format(noption) if noption else '',
                os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'tests',
                    'test_plot.py')))):
            raise RuntimeError('Tracing did not complete successfully')
    stop_time = datetime.datetime.now()
    if not no_print:
        print('Auto-generation of exceptions documentation time: {0}'.format(
            putil.misc.elapsed_time_string(start_time, stop_time)
        ))
        module_prefix = 'putil.plot.csv_source.CsvSource.'
        callable_names = (
            '__init__',
            'file_name',
            'dfilter',
            'indep_col_label',
            'dep_col_label',
            'indep_min',
            'indep_max',
            'fproc',
            'fproc_eargs',
            'indep_var',
            'dep_var'
        )
        for callable_name in callable_names:
            callable_name = module_prefix+callable_name
            print('\nCallable: {0}'.format(callable_name))
            print(exdoc_obj.get_sphinx_doc(callable_name))
            print('\n')
    return copy.copy(exdoc_obj)


if __name__ == '__main__':
    trace_module(False)
