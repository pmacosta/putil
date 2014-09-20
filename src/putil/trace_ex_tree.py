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
	tobj = putil.tree.Tree()
	tobj.add([
		{'name':'dummy.root.branch1', 'data':list()},
		{'name':'dummy.root.branch2', 'data':list()},
		{'name':'dummy.root.branch1.leaf1', 'data':list()},
		{'name':'dummy.root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'dummy.root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'dummy.root.branch1.leaf2.subleaf2', 'data':list()},
	])
	tobj.collapse('dummy.root.branch1')
	tobj.copy_subtree('dummy.root.branch1', 'dummy.root.branch3')
	tobj.delete('dummy.root.branch2')
	tobj.flatten_subtree('dummy.root.branch1')
	tobj.get_children('dummy.root')
	tobj.get_data('dummy.root')
	tobj.get_leafs('dummy.root')
	tobj.get_node('dummy.root')
	tobj.get_node_children('dummy.root')
	tobj.get_node_parent('dummy.root.branch1.leaf1.subleaf1')
	tobj.get_subtree('dummy.root.branch3')
	tobj.is_root('dummy.root')
	tobj.in_tree('dummy.root')
	tobj.is_leaf('dummy.root')
	tobj.make_root('dummy.root.branch3')
	tobj.print_node('dummy.root.branch3')
	tobj.rename_node('dummy.root.branch3', 'root')

	_EXH.build_ex_tree(no_print=no_print)
	_EXH.print_ex_tree()
	_EXH.print_ex_table()


if __name__ == '__main__':
	trace_tree()
