# -*- coding: utf-8 -*-
# tree_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.tree unit tests
"""

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

	return t1obj, t2obj, t3obj


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

	def test_get_children_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_children() method raises the right exceptions """
		tree1, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.get_children('a..b')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.get_children(5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		assert test_list == len(test_list)*[True]

	def test_add_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that add() method works """
		tree1, tree2, tree3 = default_trees
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
		#
		assert test_list == len(test_list)*[True]

	def test_delete_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that delete() method raises the right exceptions """
		tree1, _, _ = default_trees
		test_list = list()
		with pytest.raises(ValueError) as excinfo:
			tree1.delete('a..b')
		test_list.append(excinfo.value.message == 'Argument `nodes` is not a valid node name')
		with pytest.raises(TypeError) as excinfo:
			tree1.delete(['t1l1', 'a..b'])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			tree1.delete(5)
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			tree1.delete(['t1l1', 5])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.delete('a.b.c')
		test_list.append(excinfo.value.message == 'Node a.b.c not in tree')
		with pytest.raises(RuntimeError) as excinfo:
			tree1.delete(['t1l1', 'a.b.c'])
		test_list.append(excinfo.value.message == 'Node a.b.c not in tree')
		assert test_list == len(test_list)*[True]

	def test_delete_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that delete() method works """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		tree1.delete('t1l1.t1l2b2')
		tree1.delete('t1l1.t1l2b1.t1l3b1b')
		tree2.delete('t2l1')
		test_list.append(tree1.get_children('t1l1') == ['t1l1.t1l2b1'])
		test_list.append(tree1.get_children('t1l1.t1l2b1') == ['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1c'])
		test_list.append(tree1.get_children('t1l1.t1l2b1.t1l3b1a') == list())
		test_list.append(tree1.get_children('t1l1.t1l2b1.t1l3b1c') == list())
		test_list.append(tree2._db == dict())	#pylint: disable=W0212
		test_list.append(tree3.get_children('t3l1') == list())
		#
		assert test_list == len(test_list)*[True]

	def test_get_node_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node() method raises the right exceptions """
		tree1, _, _ = default_trees
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
		tree1, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_node('t1l1') == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree1.get_node('t1l1.t1l2b1') == {'parent':'t1l1', 'children':['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1b', 't1l1.t1l2b1.t1l3b1c'], 'data':['Tree 1, level 2, branch 1']})
		test_list.append(tree1.get_node('t1l1.t1l2b1.t1l3b1a') == {'parent':'t1l1.t1l2b1', 'children':list(), 'data':['Tree 1, level 3, branch 1, child a']})
		assert test_list == len(test_list)*[True]

	def test_get_node_parent_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_node_parent() method raises the right exceptions """
		tree1, _, _ = default_trees
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
		tree1, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.get_node_parent('t1l1') == dict())
		test_list.append(tree1.get_node_parent('t1l1.t1l2b1') == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree1.get_node_parent('t1l1.t1l2b1.t1l3b1a') == {'parent':'t1l1', 'children':['t1l1.t1l2b1.t1l3b1a', 't1l1.t1l2b1.t1l3b1b', 't1l1.t1l2b1.t1l3b1c'], 'data':['Tree 1, level 2, branch 1']})
		assert test_list == len(test_list)*[True]

	def test_get_data_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that get_data() method raises the right exceptions """
		tree1, _, _ = default_trees
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
		tree1, tree2, tree3 = default_trees
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
		tree1, _, _ = default_trees
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
		tree1, _, _ = default_trees
		test_list = list()
		test_list.append(tree1.in_tree('x.x.x') == False)
		test_list.append(tree1.in_tree('t1l1.t1l2b1') == True)
		assert test_list == len(test_list)*[True]

	def test_print_node_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that print_node() method raises the right exceptions """
		tree1, _, _ = default_trees
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
		tree1, tree2, tree3 = default_trees
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
		tree1, _, _ = default_trees
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
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.is_root('t1l1') == True)
		test_list.append(tree2.is_root('t2l1.t2l2b1') == False)
		test_list.append(tree2.is_root('t2l1.t2l2b1.t2l3b1b') == False)
		test_list.append(tree3.is_root('t3l1') == True)
		assert test_list == len(test_list)*[True]

	def test_is_leaf_errors(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that is_leaf() method raises the right exceptions """
		tree1, _, _ = default_trees
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
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.is_leaf('t1l1') == False)
		test_list.append(tree2.is_leaf('t2l1.t2l2b1') == False)
		test_list.append(tree2.is_leaf('t2l1.t2l2b1.t2l3b1b') == True)
		test_list.append(tree3.is_leaf('t3l1') == True)
		assert test_list == len(test_list)*[True]

	def test_root_node_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _ = default_trees
		tree4 = putil.tree.Tree()
		test_list = list()
		test_list.append(tree1.root_node == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree4.root_node == None)
		assert test_list == len(test_list)*[True]

	def test_root_name_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _ = default_trees
		tree4 = putil.tree.Tree()
		test_list = list()
		test_list.append(tree1.root_name == 't1l1')
		test_list.append(tree4.root_name == None)
		assert test_list == len(test_list)*[True]

	def test_cannot_delete_attributes(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _ = default_trees
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
		tree1, tree2, tree3 = default_trees
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
		t1obj.collapse(t1obj.root_name)
		test_list.append(str(t1obj) == u'l0\n└l1 (*)\n └l2\n  ├l3b1\n  │├l4b1b1.l5b1b1b1\n  ││├l6b1b1b1b1\n  ││└l6b1b1b1b2\n  │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1\n  └l3b2.l4b2b1 (*)\n   └l5b2b1b1'.encode('utf-8'))
		test_list.append(t1obj.get_data('l0.l1') == ['hello'])
		test_list.append(t1obj.get_data('l0.l1.l2.l3b2.l4b2b1') == [5])
		assert test_list == len(test_list)*[True]
