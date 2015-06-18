# trace_ex_tree.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

from __future__ import print_function
import copy, datetime, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
    """ Trace tree module exceptions """
    noption = os.environ.get('NOPTION', None)
    start_time = datetime.datetime.now()
    with putil.exdoc.ExDocCxt(
            exclude=['_pytest', 'execnet']
    ) as exdoc_obj:
        if pytest.main('-x {0}{1}'.format(
                '{0} '.format(noption) if noption else '',
                os.path.realpath(os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'tests',
                    'test_tree.py')))):
            raise RuntimeError('Tracing did not complete successfully')
    stop_time = datetime.datetime.now()
    if not no_print:
        print('Auto-generation of exceptions documentation time: {0}'.format(
            putil.misc.elapsed_time_string(start_time, stop_time)
        ))
        module_prefix = 'putil.tree.Tree.'
        callable_names = (
            '__init__',
            'add_nodes',
            'collapse_subtree',
            'copy_subtree',
            'delete_subtree',
            'delete_prefix',
            'flatten_subtree',
            'get_children',
            'get_data',
            'get_leafs',
            'get_node',
            'get_node_children',
            'get_node_parent',
            'get_subtree',
            'is_root',
            'in_tree',
            'is_leaf',
            'make_root',
            'print_node',
            'rename_node',
            'search_tree'
        )
        for callable_name in callable_names:
            callable_name = module_prefix+callable_name
            print('\nCallable: {0}'.format(callable_name))
            print(exdoc_obj.get_sphinx_doc(callable_name))
            print('\n')
    return copy.copy(exdoc_obj)


if __name__ == '__main__':
    trace_module(False)
