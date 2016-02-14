# trace_ex_eng_wave_core.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace eng wave module exceptions """
    mname = 'wave_functions'
    fname = 'eng'
    module_prefix = 'putil.{0}.{1}.'.format(fname, mname)
    callable_names = (
        'acos',
        'acosh',
        'asin',
        'asinh',
        'atan',
        'atanh',
        'ceil',
        'cos',
        'cosh',
        'db',
        'to_complex',
        'to_float',
        'to_int',
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print,
    )


if __name__ == '__main__':
    trace_module(False)
