# trace_my_module_1.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410

##
# Option 1: use already written test bench
##

from __future__ import print_function
import copy, os, pytest, putil.exdoc

def trace_module(no_print=True):
    """ Trace my_module exceptions """
    pwd = os.path.dirname(__file__)
    script_name = repr(os.path.join(pwd, 'test_my_module.py'))
    with putil.exdoc.ExDocCxt() as exdoc_obj:
        if pytest.main('-s -vv -x {0}'.format(script_name)):
            raise RuntimeError(
                'Tracing did not complete successfully'
            )
    if not no_print:
        module_prefix = 'docs.support.my_module.'
        callable_names = ['func', 'MyClass.value']
        for callable_name in callable_names:
            callable_name = module_prefix+callable_name
            print('\nCallable: {0}'.format(callable_name))
            print(exdoc_obj.get_sphinx_doc(callable_name, width=70))
            print('\n')
    return copy.copy(exdoc_obj)

if __name__ == '__main__':
    trace_module(False)
