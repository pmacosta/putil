# -*- coding: utf-8 -*-
# tree_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.tree unit tests
"""

import copy
import pytest

import putil.misc
import putil.tree


###
# Tests for CsvFile
###

@pytest.fixture
def default_trees():	#pylint: disable=R0914
	""" Provides a default tree to be used in teseting the putil.tree.TreeNode() class """
	#
	# Tree1				Tree2			Tree3		Tree4
	# t1l1 (*)			t2l1 (*)		t3l1 (*)	root
	# ├t1l2b1 (*)		├t2l2b1 (*)                 ├branch1 (*)
	# │├t1l3b1a (*)		│├t2l3b1a (*)               │├leaf1
	# │├t1l3b1b (*)		│├t2l3b1b (*)               ││└subleaf1 (*)
	# │└t1l3b1c (*)		│└t2l3b1c (*)               │└leaf2 (*)
	# └t1l2b2 (*)		└t2l2b2 (*)                 │ └subleaf2
	#  ├t1l3b2a (*)		 ├t2l3b2a (*)               └branch2
	#  ├t1l3b2b (*)		 ├t2l3b2b (*)
	#  └t1l3b2c (*)		 └t2l3b2c (*)
	t1obj = putil.tree.Tree()
	t1obj.add({'name':'t1l1', 'data':'Tree 1, level 1'})
	t1obj.add([
		{'name':'t1l1.t1l2b1', 'data':'Tree 1, level 2, branch 1'},
		{'name':'t1l1.t1l2b2', 'data':'Tree 1, level 2, branch 2'},
		{'name':'t1l1.t1l2b1.t1l3b1a', 'data':'Tree 1, level 3, branch 1, child a'},
		{'name':'t1l1.t1l2b1.t1l3b1b', 'data':'Tree 1, level 3, branch 1, child b'},
		{'name':'t1l1.t1l2b1.t1l3b1c', 'data':'Tree 1, level 3, branch 1, child c'},
		{'name':'t1l1.t1l2b2.t1l3b2a', 'data':'Tree 1, level 3, branch 2, child a'},
		{'name':'t1l1.t1l2b2.t1l3b2b', 'data':'Tree 1, level 3, branch 2, child b'},
		{'name':'t1l1.t1l2b2.t1l3b2c', 'data':'Tree 1, level 3, branch 2, child c'},
	])

	###
	t2obj = putil.tree.Tree()
	#
	t2obj.add({'name':'t2l1.t2l2b1.t2l3b1a', 'data':'Tree 2, level 3, branch 1, child a'})
	t2obj.add({'name':'t2l1.t2l2b1.t2l3b1b', 'data':'Tree 2, level 3, branch 1, child b'})
	t2obj.add({'name':'t2l1.t2l2b1.t2l3b1c', 'data':'Tree 2, level 3, branch 1, child c'})
	#
	t2obj.add({'name':'t2l1', 'data':'Tree 2, level 1'})
	#
	t2obj.add({'name':'t2l1.t2l2b1', 'data':'Tree 2, level 2, branch 1'})
	#
	t2obj.add([
		{'name':'t2l1.t2l2b2.t2l3b2a', 'data':'Tree 2, level 3, branch 2, child a'},
		{'name':'t2l1.t2l2b2.t2l3b2b', 'data':'Tree 2, level 3, branch 2, child b'},
		{'name':'t2l1.t2l2b2.t2l3b2c', 'data':'Tree 2, level 3, branch 2, child c'},
	])
	#
	t2obj.add({'name':'t2l1.t2l2b2', 'data':'Tree 2, level 2, branch 2'})
	#
	t3obj = putil.tree.Tree()
	t3obj.add([{'name':'t3l1', 'data':'Tree 3, level 1'}, {'name':'t3l1.t3l2', 'data':'Tree 2, level 2'}])
	t3obj.delete('t3l1.t3l2')

	t4obj = putil.tree.Tree()
	t4obj.add([
		{'name':'root.branch1', 'data':5},
		{'name':'root.branch1', 'data':7},
		{'name':'root.branch2', 'data':list()},
		{'name':'root.branch1.leaf1', 'data':list()},
		{'name':'root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'root.branch1.leaf2.subleaf2', 'data':list()},
	])

	return t1obj, t2obj, t3obj, t4obj


class TestTreeNode(object):	#pylint: disable=W0232,R0904
	""" Tests for CsvFile class """

	def test_add_errors(self):	#pylint: disable=C0103,R0201
		""" Test that add() method raises the right exceptions """
		obj = putil.tree.Tree()
		test_list = list()
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':5}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':{'key':'a'}}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':{'name':'a'}}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':{'data':'a'}}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':{'name':'a.b', 'data':'a', 'edata':5}}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':[{'name':'a.c', 'data':'a'}, {'key':'a'}]}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':[{'name':'a.c', 'data':'a'}, {'name':'a'}]}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':[{'name':'a.c', 'data':'a'}, {'data':'a'}]}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':[{'name':'a.c', 'data':'a'}, {'name':'a.b', 'data':'a', 'edata':5}]}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.add, {'nodes':[{'name':'a.c', 'data':'a'}, {'name':'d.e', 'data':'a'}]}, ValueError, 'Illegal node name: d.e'))
		assert test_list == len(test_list)*[True]

	def test_add_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that add() method works """
		tree1, tree2, tree3, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_children('t1l1') == ['t1l1.t1l2b1', 't1l1.t1l2b2'])
		test_list.append(tree1.get_children('t1l1.t1l2b1') == ['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1b', 't1l1.t1l2b1.t1l3b1c'])
		test_list.append(tree1.get_children('t1l1.t1l2b1.t1l3b1a') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b1.t1l3b1b') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b1.t1l3b1c') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b2') == ['t1l1.t1l2b2.t1l3b2a', 't1l1.t1l2b2.t1l3b2b', 't1l1.t1l2b2.t1l3b2c'])
		test_list.append(tree1.get_children('t1l1.t1l2b2.t1l3b2a') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b2.t1l3b2b') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b2.t1l3b2c') == list())
		test_list.append(tree2.get_children('t2l1') == ['t2l1.t2l2b1', 't2l1.t2l2b2'])
		test_list.append(tree2.get_children('t2l1.t2l2b1') == ['t2l1.t2l2b1.t2l3b1a', 't2l1.t2l2b1.t2l3b1b', 't2l1.t2l2b1.t2l3b1c'])
		test_list.append(tree2.get_children('t2l1.t2l2b1.t2l3b1a') == list())
		test_list.append(tree2.get_children('t2l1.t2l2b1.t2l3b1b') == list())
		test_list.append(tree2.get_children('t2l1.t2l2b1.t2l3b1c') == list())
		test_list.append(tree2.get_children('t2l1.t2l2b2') == ['t2l1.t2l2b2.t2l3b2a', 't2l1.t2l2b2.t2l3b2b', 't2l1.t2l2b2.t2l3b2c'])
		test_list.append(tree2.get_children('t2l1.t2l2b2.t2l3b2a') == list())
		test_list.append(tree2.get_children('t2l1.t2l2b2.t2l3b2b') == list())
		test_list.append(tree2.get_children('t2l1.t2l2b2.t2l3b2c') == list())
		test_list.append(tree3.get_children('t3l1') == list())
		# Test that data id's are different
		tree4 = putil.tree.Tree()
		ndata = [1, 2, 3]
		tree4.add([{'name':'root', 'data':list()}, {'name':'root.leaf1', 'data':ndata}, {'name':'root.leaf2', 'data':ndata}])
		test_list.append(id(tree4.get_data('root.leaf1')) != id(tree4.get_data('root.leaf2')))
		#
		assert test_list == len(test_list)*[True]

	def test_collapse_errors(self):	#pylint: disable=C0103,R0201
		""" Test that collapse() method raises the right exceptions """
		obj = putil.tree.Tree()
		test_list = list()
		test_list.append(putil.misc.trigger_exception(obj.collapse, {'name':5}, TypeError, 'Argument `name` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.collapse, {'name':'a.b..c'}, ValueError, 'Argument `name` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(obj.collapse, {'name':'a.b.c'}, RuntimeError, 'Node a.b.c not in tree'))
		assert test_list == len(test_list)*[True]

	def test_collapse_works(self):	#pylint: disable=C0103,R0201,W0621
		""" Test that collapse method works """
		test_list = list()
		t1obj = putil.tree.Tree()
		t1obj.add([
			{'name':'l0.l1', 'data':'hello'},
			{'name':'l0.l1.l2.l3b2.l4b2b1', 'data':5},
			{'name':'l0.l1.l2.l3b2.l4b2b1.l5b2b1b1', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b1', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b2', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1', 'data':list()},
		])
		# Original tree       Collapsed tree
		# l0                  l0
		# └l1 (*)             └l1 (*)
		#  └l2                 └l2
		#   ├l3b1               ├l3b1
		#   │├l4b1b1            │├l4b1b1.l5b1b1b1
		#   ││└l5b1b1b1         ││├l6b1b1b1b1
		#   ││ ├l6b1b1b1b1      ││└l6b1b1b1b2
		#   ││ └l6b1b1b1b2      │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1
		#   │└l5b1b1            └l3b2.l4b2b1 (*)
		#   │ └l5b1b1b2          └l5b2b1b1
		#   │  └l6b1b1b2b1
		#   │   └l7b1b1b2b1b1
		#   └l3b2
		#    └l4b2b1 (*)
		#     └l5b2b1b1
		t1obj.collapse(t1obj.root_name)
		test_list.append(str(t1obj) == u'l0\n└l1 (*)\n └l2\n  ├l3b1\n  │├l4b1b1.l5b1b1b1\n  ││├l6b1b1b1b1\n  ││└l6b1b1b1b2\n  │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1\n  └l3b2.l4b2b1 (*)\n   └l5b2b1b1'.encode('utf-8'))
		test_list.append(t1obj.get_data('l0.l1') == ['hello'])
		test_list.append(t1obj.get_data('l0.l1.l2.l3b2.l4b2b1') == [5])
		assert test_list == len(test_list)*[True]

	def test_copy_subtree_errors(self):	#pylint: disable=C0103,R0201
		""" Test that copy_subtree() method raises the right exceptions """
		obj = putil.tree.Tree()
		obj.add([{'name':'root', 'data':list()}, {'name':'root.leaf1', 'data':5}, {'name':'root.leaf2', 'data':7}])
		test_list = list()
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':5, 'dest_node':'root.x'}, TypeError, 'Argument `source_node` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':'.x.y', 'dest_node':'root.x'}, ValueError, 'Argument `source_node` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':'hello', 'dest_node':'root.x'}, RuntimeError, 'Node hello not in tree'))
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':'root.leaf1', 'dest_node':5}, TypeError, 'Argument `dest_node` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':'root.leaf1', 'dest_node':'x..y'}, ValueError, 'Argument `dest_node` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(obj.copy_subtree, {'source_node':'root.leaf1', 'dest_node':'teto.leaf2'}, RuntimeError, 'Illegal root in destination node'))
		assert test_list == len(test_list)*[True]

	def test_copy_subtree_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that copy_subtree() method works """
		_, _, _, tree4 = default_trees
		test_list = list()
		tree4.copy_subtree('root.branch1', 'root.branch2.branch3')
		# Original tree   Copied sub-tree
		# root            root
		# ├branch1 (*)    ├branch1 (*)
		# │├leaf1         │├leaf1
		# ││└subleaf1 (*) ││└subleaf1 (*)
		# │└leaf2 (*)     │└leaf2 (*)
		# │ └subleaf2     │ └subleaf2
		# └branch2        └branch2
		#                  └branch3 (*)
		#                   ├leaf1
		#                   │└subleaf1 (*)
        #                   └leaf2 (*)
        #                    └subleaf2
		# Test tree relationship
		test_list.append(str(tree4) == u'root\n├branch1 (*)\n│├leaf1\n││└subleaf1 (*)\n│└leaf2 (*)\n│ └subleaf2\n└branch2\n └branch3 (*)\n  ├leaf1\n  │└subleaf1 (*)\n  └leaf2 (*)\n   └subleaf2'.encode('utf-8'))
		# Test that there are no pointers between source and destination data
		test_list.append(id(tree4.get_data('root.branch1')) != id(tree4.get_data('root.branch2.branch3')))
		test_list.append(id(tree4.get_data('root.branch1.leaf1')) != id(tree4.get_data('root.branch2.branch3.leaf1')))
		test_list.append(id(tree4.get_data('root.branch1.leaf1.subleaf1')) != id(tree4.get_data('root.branch2.branch3.leaf1.subleaf1')))
		test_list.append(id(tree4.get_data('root.branch1.leaf2')) != id(tree4.get_data('root.branch2.branch3.leaf2')))
		test_list.append(id(tree4.get_data('root.branch1.leaf2.subleaf2')) != id(tree4.get_data('root.branch2.branch3.leaf2.subleaf2')))
		# Test that data values are the same
		test_list.append(tree4.get_data('root.branch1') == tree4.get_data('root.branch2.branch3'))
		test_list.append(tree4.get_data('root.branch1.leaf1') == tree4.get_data('root.branch2.branch3.leaf1'))
		test_list.append(tree4.get_data('root.branch1.leaf1.subleaf1') == tree4.get_data('root.branch2.branch3.leaf1.subleaf1'))
		test_list.append(tree4.get_data('root.branch1.leaf2') == tree4.get_data('root.branch2.branch3.leaf2'))
		test_list.append(tree4.get_data('root.branch1.leaf2.subleaf2') == tree4.get_data('root.branch2.branch3.leaf2.subleaf2'))
		assert test_list == len(test_list)*[True]

	def test_delete_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that delete() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':'a..b'}, ValueError, 'Argument `nodes` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':['t1l1', 'a..b']}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':5}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':['t1l1', 5]}, TypeError, 'Argument `nodes` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':'a.b.c'}, RuntimeError, 'Node a.b.c not in tree'))
		test_list.append(putil.misc.trigger_exception(tree1.delete, {'nodes':['t1l1', 'a.b.c']}, RuntimeError, 'Node a.b.c not in tree'))
		assert test_list == len(test_list)*[True]

	def test_delete_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that delete() method works """
		tree1, tree2, _, _ = default_trees
		test_list = list()
		tree1.delete('t1l1.t1l2b2')
		tree1.delete('t1l1.t1l2b1.t1l3b1b')
		tree2.delete('t2l1')
		test_list.append(str(tree1) == u't1l1 (*)\n└t1l2b1 (*)\n ├t1l3b1a (*)\n └t1l3b1c (*)'.encode('utf-8'))
		test_list.append(str(tree2) == '')
		#
		assert test_list == len(test_list)*[True]

	def test_flatten_subtree_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that flatten_subtree() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(putil.misc.trigger_exception(tree1.flatten_subtree, {'name':'a..b'}, ValueError, 'Argument `name` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(tree1.flatten_subtree, {'name':5}, TypeError, 'Argument `name` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(tree1.flatten_subtree, {'name':'a.b.c'}, RuntimeError, 'Node a.b.c not in tree'))
		assert test_list == len(test_list)*[True]

	def test_flatten_subtree_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that flatten_subtree method works """
		_, _, _, tree4 = default_trees
		test_list = list()
		tree4.add([{'name':'root.branch1.leaf1.subleaf2', 'data':list()},
		          {'name':'root.branch2.leaf1', 'data':'loren ipsum'},
		          {'name':'root.branch2.leaf1.another_subleaf1', 'data':list()},
		          {'name':'root.branch2.leaf1.another_subleaf2', 'data':list()}
		])
		odata = copy.deepcopy(tree4.get_data('root.branch1.leaf1.subleaf1'))
		tree4.flatten_subtree('root.branch1.leaf1')
		test_list.append(str(tree4) == u'root\n├branch1 (*)\n│├leaf1.subleaf1 (*)\n│├leaf1.subleaf2\n│└leaf2 (*)\n│ └subleaf2\n└branch2\n └leaf1 (*)\n  ├another_subleaf1\n  └another_subleaf2'.encode('utf-8'))
		test_list.append(tree4.get_data('root.branch1.leaf1.subleaf1') == odata)
		tree4.flatten_subtree('root.branch2.leaf1')
		test_list.append(str(tree4) == u'root\n├branch1 (*)\n│├leaf1.subleaf1 (*)\n│├leaf1.subleaf2\n│└leaf2 (*)\n│ └subleaf2\n└branch2\n └leaf1 (*)\n  ├another_subleaf1\n  └another_subleaf2'.encode('utf-8'))
		assert test_list == len(test_list)*[True]

	def test_get_children_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_children() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(putil.misc.trigger_exception(tree1.get_children, {'name':'a..b'}, ValueError, 'Argument `name` is not a valid node name'))
		test_list.append(putil.misc.trigger_exception(tree1.get_children, {'name':5}, TypeError, 'Argument `name` is of the wrong type'))
		test_list.append(putil.misc.trigger_exception(tree1.get_children, {'name':'a.b.c'}, RuntimeError, 'Node a.b.c not in tree'))
		assert test_list == len(test_list)*[True]

	def test_get_node_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.get_node('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.get_node(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.get_node('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]


	def test_get_node_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node() method works """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_node('t1l1') == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree1.get_node('t1l1.t1l2b1') == {'parent':'t1l1', 'children':['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1b', 't1l1.t1l2b1.t1l3b1c'], 'data':['Tree 1, level 2, branch 1']})
		test_list.append(tree1.get_node('t1l1.t1l2b1.t1l3b1a') == {'parent':'t1l1.t1l2b1', 'children':list(), 'data':['Tree 1, level 3, branch 1, child a']})
		assert test_list == len(test_list)*[True]

	def test_get_node_parent_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node_parent() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.get_node_parent('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.get_node_parent(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.get_node_parent('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]

	def test_get_node_parent_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node_parent() method works """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_node_parent('t1l1') == dict())
		test_list.append(tree1.get_node_parent('t1l1.t1l2b1') == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree1.get_node_parent('t1l1.t1l2b1.t1l3b1a') == {'parent':'t1l1', 'children':['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1b', 't1l1.t1l2b1.t1l3b1c'], 'data':['Tree 1, level 2, branch 1']})
		assert test_list == len(test_list)*[True]

	def test_get_data_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_data() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.get_data('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.get_data(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.get_data('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]

	def test_get_data_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_data() method works """
		tree1, tree2, tree3, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_data('t1l1') == ['Tree 1, level 1'])
		test_list.append(tree1.get_data('t1l1.t1l2b1') == ['Tree 1, level 2, branch 1'])
		test_list.append(tree1.get_data('t1l1.t1l2b1.t1l3b1a') == ['Tree 1, level 3, branch 1, child a'])
		test_list.append(tree1.get_data('t1l1.t1l2b1.t1l3b1b') == ['Tree 1, level 3, branch 1, child b'])
		test_list.append(tree1.get_data('t1l1.t1l2b1.t1l3b1c') == ['Tree 1, level 3, branch 1, child c'])
		test_list.append(tree1.get_data('t1l1.t1l2b2') == ['Tree 1, level 2, branch 2'])
		test_list.append(tree1.get_data('t1l1.t1l2b2.t1l3b2a') == ['Tree 1, level 3, branch 2, child a'])
		test_list.append(tree1.get_data('t1l1.t1l2b2.t1l3b2b') == ['Tree 1, level 3, branch 2, child b'])
		test_list.append(tree1.get_data('t1l1.t1l2b2.t1l3b2c') == ['Tree 1, level 3, branch 2, child c'])
		test_list.append(tree2.get_data('t2l1') == ['Tree 2, level 1'])
		test_list.append(tree2.get_data('t2l1.t2l2b1') == ['Tree 2, level 2, branch 1'])
		test_list.append(tree2.get_data('t2l1.t2l2b1.t2l3b1a') == ['Tree 2, level 3, branch 1, child a'])
		test_list.append(tree2.get_data('t2l1.t2l2b1.t2l3b1b') == ['Tree 2, level 3, branch 1, child b'])
		test_list.append(tree2.get_data('t2l1.t2l2b1.t2l3b1c') == ['Tree 2, level 3, branch 1, child c'])
		test_list.append(tree2.get_data('t2l1.t2l2b2') == ['Tree 2, level 2, branch 2'])
		test_list.append(tree2.get_data('t2l1.t2l2b2.t2l3b2a') == ['Tree 2, level 3, branch 2, child a'])
		test_list.append(tree2.get_data('t2l1.t2l2b2.t2l3b2b') == ['Tree 2, level 3, branch 2, child b'])
		test_list.append(tree2.get_data('t2l1.t2l2b2.t2l3b2c') == ['Tree 2, level 3, branch 2, child c'])
		test_list.append(tree3.get_data('t3l1') == ['Tree 3, level 1'])
		tree4 = putil.tree.Tree()
		tree4.add({'name':'t4l1', 'data':list()})
		test_list.append(tree4.get_data('t4l1') == list())
		tree4.add([{'name':'t4l1', 'data':'Hello'}, {'name':'t4l1', 'data':'world'}])
		tree4.add({'name':'t4l1', 'data':'!'})
		test_list.append(tree4.get_data('t4l1') == ['Hello', 'world', '!'])
		assert test_list == len(test_list)*[True]

	def test_in_tree_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that in_tree() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.in_tree('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.in_tree(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		assert test_list == len(test_list)*[True]

	def test_in_tree_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that in_tree() method works """
		tree1, _, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.in_tree('x.x.x') == False)
		test_list.append(tree1.in_tree('t1l1.t1l2b1') == True)
		assert test_list == len(test_list)*[True]

	def test_print_node_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that print_node() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.print_node('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.print_node(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.print_node('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]

	def test_print_node_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the method __str__ works as expected """
		tree1, tree2, tree3, _ = default_trees
		obj = putil.tree.Tree()
		obj.add([{'name':'dtree', 'data':list()}, {'name':'dtree.my_child', 'data':'Tree 2, level 2'}])
		test_list = list()
		#
		test_list.append(tree1.print_node('t1l1') == 'Name: t1l1\nParent: None\nChildren: t1l2b1, t1l2b2\nData: Tree 1, level 1')
		tree2.add({'name':'t2l1.t2l2b1.t2l3b1b', 'data':14.3})
		test_list.append(tree2.print_node('t2l1.t2l2b1.t2l3b1b') == "Name: t2l1.t2l2b1.t2l3b1b\nParent: t2l1.t2l2b1\nChildren: None\nData: ['Tree 2, level 3, branch 1, child b', 14.3]")
		test_list.append(tree3.print_node('t3l1') == 'Name: t3l1\nParent: None\nChildren: None\nData: Tree 3, level 1')
		test_list.append(obj.print_node('dtree') == 'Name: dtree\nParent: None\nChildren: my_child\nData: None')
		#
		assert test_list == len(test_list)*[True]

	def test_is_root_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that is_root() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.is_root('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.is_root(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.is_root('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]

	def test_is_root(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property is_root works as expected """
		tree1, tree2, tree3, _ = default_trees
		test_list = list()
		test_list.append(tree1.is_root('t1l1') == True)
		test_list.append(tree2.is_root('t2l1.t2l2b1') == False)
		test_list.append(tree2.is_root('t2l1.t2l2b1.t2l3b1b') == False)
		test_list.append(tree3.is_root('t3l1') == True)
		assert test_list == len(test_list)*[True]

	def test_is_leaf_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that is_leaf() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.is_leaf('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.is_leaf(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.is_leaf('a.b')
		test_list.append(excinfo.value.message == 'Node a.b not in tree')
		assert test_list == len(test_list)*[True]

	def test_is_leaf(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property is_leaf works as expected """
		tree1, tree2, tree3, _ = default_trees
		test_list = list()
		test_list.append(tree1.is_leaf('t1l1') == False)
		test_list.append(tree2.is_leaf('t2l1.t2l2b1') == False)
		test_list.append(tree2.is_leaf('t2l1.t2l2b1.t2l3b1b') == True)
		test_list.append(tree3.is_leaf('t3l1') == True)
		assert test_list == len(test_list)*[True]

	def test_root_node_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _, _ = default_trees
		tree4 = putil.tree.Tree()
		test_list = list()
		test_list.append(tree1.root_node == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree4.root_node == None)
		assert test_list == len(test_list)*[True]

	def test_root_name_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _, _ = default_trees
		tree4 = putil.tree.Tree()
		test_list = list()
		test_list.append(tree1.root_name == 't1l1')
		test_list.append(tree4.root_name == None)
		assert test_list == len(test_list)*[True]

	def test_cannot_delete_attributes(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _, _ = default_trees
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del tree1.root_node
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.root_name
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == len(test_list)*[True]

	def test_str_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that ppstr method works """
		tree1, tree2, tree3, _ = default_trees
		test_list = list()
		tree1.add([
			{'name':'t1l1.t1l2b1.t1l3b1a.leaf1', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.subleaf4', 'data':list()}
		])
		test_list.append(str(tree1) == u't1l1 (*)\n├t1l2b1 (*)\n│├t1l3b1a (*)\n││└leaf1\n│├t1l3b1b (*)\n│└t1l3b1c (*)\n│ └leaf2\n│  ├leaf3\n│  └subleaf4\n└t1l2b2 (*)\n ├t1l3b2a (*)\n ├t1l3b2b (*)\n └t1l3b2c (*)'.encode('utf-8'))
		test_list.append(str(tree2) == u't2l1 (*)\n├t2l2b1 (*)\n│├t2l3b1a (*)\n│├t2l3b1b (*)\n│└t2l3b1c (*)\n└t2l2b2 (*)\n ├t2l3b2a (*)\n ├t2l3b2b (*)\n └t2l3b2c (*)'.encode('utf-8'))
		test_list.append(str(tree3) == u't3l1 (*)'.encode('utf-8'))
		tree3.add({'name':'t3l1.leaf1', 'data':list()})
		test_list.append(str(tree3) == u't3l1 (*)\n└leaf1'.encode('utf-8'))
		tree3.add({'name':'t3l1.leaf2', 'data':list()})
		test_list.append(str(tree3) == u't3l1 (*)\n├leaf1\n└leaf2'.encode('utf-8'))
		assert test_list == len(test_list)*[True]

