# trace_ex_tree.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0212

import docs.support.trace_support


def trace_module(no_print=True):
    """ Trace tree module exceptions """
    mname = 'tree'
    fname = 'tree'
    module_prefix = 'putil.{0}.Tree.'.format(mname)
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
    )
    return docs.support.trace_support.run_trace(
        mname, fname, module_prefix, callable_names, no_print
    )


if __name__ == '__main__':
    trace_module(False)
