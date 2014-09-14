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
	_EXH = putil.exh.ExHandle(putil.tree.Tree)
	obj = putil.tree.Tree()
	obj.add([
		{'name':'root.branch1', 'data':list()},
		{'name':'root.branch2', 'data':list()},
		{'name':'root.branch1.leaf1', 'data':list()},
		{'name':'root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'root.branch1.leaf2.subleaf2', 'data':list()},
	])
	print 'Original tree'
	print str(obj)
	obj.collapse('root.branch1')
	print 'Collapsed tree'
	print str(obj)
	obj.copy_subtree('root.branch1', 'root.branch3')
	print 'Copied tree'
	print str(obj)
	obj.delete('root.branch2')
	print 'Deleted tree'
	print str(obj)
	obj.flatten_subtree('root.branch1')
	print 'Flattened tree'
	print str(obj)
	obj.get_node('root')
	obj.get_node_children('root')
	obj.get_node_parent('root.branch1.leaf1.subleaf1')
	obj.get_children('root')
	obj.get_data('root')
	obj.in_tree('root')
	obj.is_root('root')
	obj.is_leaf('root')
	obj.make_root('root.branch1.leaf2')
	print 'Make root tree'
	print str(obj)

	_EXH.build_ex_tree(no_print=no_print)
	_EXH.print_ex_tree()
	_EXH.print_ex_table()


if __name__ == '__main__':
	trace_tree()
