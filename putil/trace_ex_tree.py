# trace_ex_tree
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy

import putil.exh
import putil.misc
import putil.tree
import putil.exdoc


def trace_tree(no_print=False):
	""" Trace Tree class """
	if not no_print:
		print putil.misc.pcolor('Tracing Tree', 'blue')
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	tobj = putil.tree.Tree()
	tobj.add_nodes([
		{'name':'dummy.root.branch1', 'data':list()},
		{'name':'dummy.root.branch2', 'data':list()},
		{'name':'dummy.root.branch1.leaf1', 'data':list()},
		{'name':'dummy.root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'dummy.root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'dummy.root.branch1.leaf2.subleaf2', 'data':list()},
	])
	tobj.collapse_subtree('dummy.root.branch1')
	tobj.copy_subtree('dummy.root.branch1', 'dummy.root.branch3')
	tobj.delete_subtree('dummy.root.branch2')
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
	tobj.nodes	#pylint: disable=W0104
	tobj.root_node	#pylint: disable=W0104
	tobj.root_name	#pylint: disable=W0104

	exobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=no_print)
	if not no_print:
		exobj.print_ex_tree()
		exobj.print_ex_table()
	return copy.copy(exobj)


if __name__ == '__main__':
	trace_tree()
