# trace_ex_tree		pylint: disable=C0111
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details

import putil.exh
import putil.misc
import putil.tree

_EXH = None

def trace_tree(no_print=False):
	""" Trace Tree class """
	global _EXH	#pylint: disable=W0603
	if not no_print:
		print putil.misc.pcolor('Tracing Tree', 'blue')
	_EXH = putil.exh.ExHandle(putil.tree.Tree)
	obj = putil.tree.Tree()
	obj.add([
		{'name':'dummy.root.branch1', 'data':list()},
		{'name':'dummy.root.branch2', 'data':list()},
		{'name':'dummy.root.branch1.leaf1', 'data':list()},
		{'name':'dummy.root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'dummy.root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'dummy.root.branch1.leaf2.subleaf2', 'data':list()},
	])
	obj.collapse('dummy.root.branch1')
	obj.copy_subtree('dummy.root.branch1', 'dummy.root.branch3')
	obj.delete('dummy.root.branch2')
	obj.flatten_subtree('dummy.root.branch1')
	obj.get_children('dummy.root')
	obj.get_data('dummy.root')
	obj.get_leafs('dummy.root')
	obj.get_node('dummy.root')
	obj.get_node_children('dummy.root')
	obj.get_node_parent('dummy.root.branch1.leaf1.subleaf1')
	obj.get_subtree('dummy.root.branch3')
	obj.is_root('dummy.root')
	obj.in_tree('dummy.root')
	obj.is_leaf('dummy.root')
	obj.make_root('dummy.root.branch3')
	obj.print_node('dummy.root.branch3')
	obj.remove_prefix('dummy')
	obj.rename_node('root.branch3.leaf1', 'root.branch3.mapleleaf2')

	_EXH.build_ex_tree(no_print=no_print)
	_EXH.print_ex_tree()
	_EXH.print_ex_table()


if __name__ == '__main__':
	trace_tree()
