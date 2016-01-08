# trace_my_module_2.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0410,W0104,W0403

###
# Option 2: manually use all callables to document
###

from __future__ import print_function
import copy, putil.exdoc, docs.support.my_module

def trace_module(no_print=True):
    """ Trace my_module_original exceptions """
    with putil.exdoc.ExDocCxt() as exdoc_obj:
        try:
            docs.support.my_module.func('John')
            obj = docs.support.my_module.MyClass()
            obj.value = 5
            obj.value
        except:
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
