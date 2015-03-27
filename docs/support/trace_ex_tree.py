# trace_ex_tree.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
	""" Trace tree module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-x '+os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..', '..', 'tests', 'test_tree.py'))):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'putil.tree.Tree.'
		callable_names = ['__init__', 'add_nodes', 'collapse_subtree', 'copy_subtree', 'delete_subtree', 'delete_prefix', 'flatten_subtree', 'get_children', 'get_data', 'get_leafs',
					'get_node', 'get_node_children', 'get_node_parent', 'get_subtree', 'is_root', 'in_tree', 'is_leaf', 'make_root', 'print_node', 'rename_node', 'search_tree']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
