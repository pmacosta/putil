# -*- coding: utf-8 -*-
# tree_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.tree unit tests
"""

import pytest

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
		with pytest.raises(TypeError) as excinfo:
			obj.add(5)
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add({'key':'a'})
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add({'name':'a'})
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add({'data':'a'})
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add({'name':'a.b', 'data':'a', 'edata':5})
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add([{'name':'a.c', 'data':'a'}, {'key':'a'}])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add([{'name':'a.c', 'data':'a'}, {'name':'a'}])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add([{'name':'a.c', 'data':'a'}, {'data':'a'}])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add([{'name':'a.c', 'data':'a'}, {'name':'a.b', 'data':'a', 'edata':5}])
		test_list.append(excinfo.value.message == 'Argument `nodes` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			obj.add([{'name':'a.c', 'data':'a'}, {'name':'d.e', 'data':'a'}])
		test_list.append(excinfo.value.message == 'Illegal node name: d.e')
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

	def test_str(self, default_trees):	#pylint: disable=C0103,R0201,W0621
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

	def test_root_node(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _ = default_trees
		tree4 = putil.tree.Tree()
		test_list = list()
		test_list.append(tree1.root_node == {'parent':'', 'children':['t1l1.t1l2b1', 't1l1.t1l2b2'], 'data':['Tree 1, level 1']})
		test_list.append(tree4.root_node == None)
		assert test_list == len(test_list)*[True]

	def test_root_name(self, default_trees):	#pylint: disable=C0103,R0201,W0621
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

	def test_ppstr_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that ppstr method works """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		tree1.children[0].children[0].children = putil.tree.TreeNode(name='leaf1')
		tree1.children[0].children[2].children = putil.tree.TreeNode(name='leaf2')
		tree1.children[0].children[2].children[0].children = [putil.tree.TreeNode(name='leaf3'), putil.tree.TreeNode(name='subleaf4')]
		test_list.append(tree1.ppstr == u't1l1 (*)\n├t1l2b1 (*)\n│├t1l3b1a (*)\n││└leaf1\n│├t1l3b1b (*)\n│└t1l3b1c (*)\n│ └leaf2\n│  ├leaf3\n│  └subleaf4\n└t1l2b2 (*)\n ├t1l3b2a (*)\n ├t1l3b2b (*)\n └t1l3b2c (*)')
		test_list.append(tree2.ppstr == u't2l1 (*)\n├t2l2b1 (*)\n│├t2l3b1a (*)\n│├t2l3b1b (*)\n│└t2l3b1c (*)\n└t2l2b2 (*)\n ├t2l3b2a (*)\n ├t2l3b2b (*)\n └t2l3b2c (*)')
		test_list.append(tree3.ppstr == u't3l1 (*)')
		tree3.children = putil.tree.TreeNode(name='leaf1')
		test_list.append(tree3.ppstr == u't3l1 (*)\n└leaf1')
		tree3.children = [putil.tree.TreeNode(name='leaf1'), putil.tree.TreeNode(name='leaf2')]
		test_list.append(tree3.ppstr == u't3l1 (*)\n├leaf1\n└leaf2')
		assert test_list == len(test_list)*[True]

	def test_collapse_works(self):	#pylint: disable=C0103,R0201,W0621
		""" Test that collapse method works """
		test_list = list()
		t1obj = putil.tree.TreeNode(name='l1')
		t2obj = putil.tree.TreeNode(name='l2b1')
		t3obj = putil.tree.TreeNode(name='l2b2')
		t1obj.children = [t2obj, t3obj]
		t4obj = putil.tree.TreeNode(name='l3b1b1')
		t2obj.children = t4obj
		t5obj = putil.tree.TreeNode(name='l3b2b1', data=5)
		t3obj.children = t5obj
		t6obj = putil.tree.TreeNode(name='l4b1b1b1')
		t4obj.children = t6obj
		t7obj = putil.tree.TreeNode(name='l4b2b1b1')
		t5obj.children = t7obj
		t8obj = putil.tree.TreeNode(name='l5b1b1b1b1')
		t9obj = putil.tree.TreeNode(name='l5b1b1b1b2')
		t6obj.children = [t8obj, t9obj]
		taobj = putil.tree.TreeNode(name='l4b1b1b2')
		t4obj.add_children(taobj)
		tbobj = putil.tree.TreeNode(name='l5b1b1b2b1')
		taobj.children = tbobj
		tcobj = putil.tree.TreeNode(name='l6b1b1b2b1b1')
		tbobj.children = tcobj
		t1obj.collapse()
		test_list.append(t1obj.ppstr == u'l1\n├l2b1.l3b1b1\n│├l4b1b1b1\n││├l5b1b1b1b1\n││└l5b1b1b1b2\n│└l4b1b1b2.l5b1b1b2b1.l6b1b1b2b1b1\n└l2b2.l3b2b1 (*)\n └l4b2b1b1')
		test_list.append(putil.tree.search_for_node(t1obj, 'l1.l2b2.l3b2b1').data == 5)
		assert test_list == len(test_list)*[True]


class TestSearchForNode(object):	#pylint: disable=W0232
	""" Tests search_for_node function """
	def test_search_for_node_errors(self):	#pylint: disable=C0103,R0201,W0621
		""" Test that function raises the right exception """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.tree.search_for_node(tree=5, name='a')
		test_list.append(excinfo.value.message == 'Argument `tree` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.search_for_node(tree=putil.tree.TreeNode(name='root'), name=5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.tree.search_for_node(tree=putil.tree.TreeNode(name='root'), name='a.b.c..d')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		# This statements should not raise any exception
		putil.tree.search_for_node(tree=putil.tree.TreeNode(name='root'), name='a')
		assert test_list == len(test_list)*[True]

	def test_search_for_node_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that function works as expected """
		tree1, tree2, tree3 = default_trees
		tobj7 = putil.tree.TreeNode(name='l4b2b1b1', data=7)
		tobj6 = putil.tree.TreeNode(name='l2b2.l3b2b1', children=tobj7, data=6)
		tobj5 = putil.tree.TreeNode(name='l4b1b1b2.l5b1b1b2b1.l6b1b1b2b1b1', data=5)
		tobj4 = putil.tree.TreeNode(name='l5b1b1b1b2', data=4)
		tobj3 = putil.tree.TreeNode(name='l5b1b1b1b1', data=3)
		tobj2 = putil.tree.TreeNode(name='l4b1b1b1', children=[tobj3, tobj4], data=2)
		tobj1 = putil.tree.TreeNode(name='l2b1.l3b1b1', children=[tobj2, tobj5], data=1)
		tobj0 = putil.tree.TreeNode(name='l1', children=[tobj1, tobj6], data=0)
		test_list = list()
		test_list.append(putil.tree.search_for_node(tree3, 'zzzz') == None)
		test_list.append(putil.tree.search_for_node(tree1, 't1l1').data == 'Tree 1, level 1')
		test_list.append(putil.tree.search_for_node(tree2, 't2l1.t2l2b2').data == 'Tree 2, level 2, branch 2')
		test_list.append(putil.tree.search_for_node(tree1, 't1l1.t1l2b1.t1l3b1c').data == 'Tree 1, level 3, branch 1, child c')
		test_list.append(putil.tree.search_for_node(tobj0, 'l1').data == 0)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1') == None)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b2') == None)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1').data == 1)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b2.l3b2b1').data == 6)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1.l4b1b1b1').data == 2)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1.l4b1b1b1.l5b1b1b1b1').data == 3)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1.l4b1b1b1.l5b1b1b1b2').data == 4)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1.l4b1b1b2.l5b1b1b2b1.l6b1b1b2b1b1').data == 5)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b2.l3b2b1.l4b2b1b1').data == 7)
		test_list.append(putil.tree.search_for_node(tobj0, 'l1.l2b1.l3b1b1.l4b1b1b2.l5b1b1b2b1.l6b1b1b2b1b1.dummy') == None)
		assert test_list == len(test_list)*[True]

	def test_build_tree_errors(self):	#pylint: disable=C0103,R0201,W0621
		""" Test error checking of build_tree function arguments """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree(5)
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([5, 7])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree({'node':'a'})
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree({'node':'a', 'data':5, 'extra_data':7})
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'b'}])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'b', 'data':5, 'extra_data':7}])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree({'node':None, 'data':5})
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([{'node':None, 'data':5}, {'node':'b', 'data':5}])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree({})
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([{}])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.build_tree([{'node':'a', 'data':5}, {}])
		test_list.append(excinfo.value.message == 'Argument `tree_info` is of the wrong type')
		# These statements should not raise an exception
		putil.tree.build_tree({'node':'a', 'data':5})
		putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'b', 'data':10}])
		assert test_list == len(test_list)*[True]

	def test_build_tree_works(self):	#pylint: disable=C0103,R0201,W0621
		""" Test error checking of build_tree function arguments """
		test_list = list()
		# 0-1
		obj = putil.tree.build_tree({'node':'a', 'data':5})
		test_list.append(obj.ppstr == 'a (*)')
		test_list.append(putil.tree.search_for_node(obj, 'a').data == 5)
		# 2-4
		obj = putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'a.b', 'data':'hello'}])
		test_list.append(obj.ppstr == u'a (*)\n└b (*)')
		test_list.append(putil.tree.search_for_node(obj, 'a').data == 5)
		test_list.append(putil.tree.search_for_node(obj, 'a.b').data == 'hello')
		# 5-8
		obj = putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'a.b', 'data':'hello'}, {'node':'a.c', 'data':37}])
		test_list.append(obj.ppstr == u'a (*)\n├b (*)\n└c (*)')
		test_list.append(putil.tree.search_for_node(obj, 'a').data == 5)
		test_list.append(putil.tree.search_for_node(obj, 'a.b').data == 'hello')
		test_list.append(putil.tree.search_for_node(obj, 'a.c').data == 37)
		# 9-14
		obj = putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'a.b', 'data':'hello'}, {'node':'a.c', 'data':37}, {'node':'a.c.d', 'data':None}, {'node':'a.c.d.e', 'data':'world!'}])
		test_list.append(obj.ppstr == u'a (*)\n├b (*)\n└c (*)\n └d\n  └e (*)')
		test_list.append(putil.tree.search_for_node(obj, 'a').data == 5)
		test_list.append(putil.tree.search_for_node(obj, 'a.b').data == 'hello')
		test_list.append(putil.tree.search_for_node(obj, 'a.c').data == 37)
		test_list.append(putil.tree.search_for_node(obj, 'a.c.d').data == None)
		test_list.append(putil.tree.search_for_node(obj, 'a.c.d.e').data == 'world!')
		# 15-20
		obj = putil.tree.build_tree([{'node':'a', 'data':5}, {'node':'a.b', 'data':'hello'}, {'node':'a.c', 'data':37}, {'node':'a.c.d', 'data':None}, {'node':'a.c.d.e', 'data':'world!'}, {'node':'a.c', 'data':999}])
		test_list.append(obj.ppstr == u'a (*)\n├b (*)\n└c (*)\n └d\n  └e (*)')
		test_list.append(putil.tree.search_for_node(obj, 'a').data == 5)
		test_list.append(putil.tree.search_for_node(obj, 'a.b').data == 'hello')
		test_list.append(putil.tree.search_for_node(obj, 'a.c').data == [37, 999])
		test_list.append(putil.tree.search_for_node(obj, 'a.c.d').data == None)
		test_list.append(putil.tree.search_for_node(obj, 'a.c.d.e').data == 'world!')
		# 21-28
		obj = putil.tree.build_tree([{'node':'aa', 'data':5}, {'node':'aa.b', 'data':'hello'}, {'node':'aa.c', 'data':37}, {'node':'dd', 'data':None}, {'node':'dd.e', 'data':'world!'}, {'node':'dd.f', 'data':999}])
		test_list.append(obj[0].ppstr == u'aa (*)\n├b (*)\n└c (*)')
		test_list.append(putil.tree.search_for_node(obj[0], 'aa').data == 5)
		test_list.append(putil.tree.search_for_node(obj[0], 'aa.b').data == 'hello')
		test_list.append(putil.tree.search_for_node(obj[0], 'aa.c').data == 37)
		test_list.append(obj[1].ppstr == u'dd\n├e (*)\n└f (*)')
		test_list.append(putil.tree.search_for_node(obj[1], 'dd').data == None)
		test_list.append(putil.tree.search_for_node(obj[1], 'dd.e').data == 'world!')
		test_list.append(putil.tree.search_for_node(obj[1], 'dd.f').data == 999)
		assert test_list == len(test_list)*[True]

