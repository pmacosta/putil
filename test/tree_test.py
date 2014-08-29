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
	t1l3b1a_obj = putil.tree.TreeNode(name='t1l3b1a', data='Tree 1, level 3, branch 1, child a')
	t1l3b1b_obj = putil.tree.TreeNode(name='t1l3b1b', data='Tree 1, level 3, branch 1, child b')
	t1l3b1c_obj = putil.tree.TreeNode(name='t1l3b1c', data='Tree 1, level 3, branch 1, child c')
	#
	t1l3b2a_obj = putil.tree.TreeNode(name='t1l3b2a', data='Tree 1, level 3, branch 2, child a')
	t1l3b2b_obj = putil.tree.TreeNode(name='t1l3b2b', data='Tree 1, level 3, branch 2, child b')
	t1l3b2c_obj = putil.tree.TreeNode(name='t1l3b2c', data='Tree 1, level 3, branch 2, child c')
	#
	t1l2b1_obj = putil.tree.TreeNode(name='t1l2b1', children=[t1l3b1a_obj, t1l3b1b_obj, t1l3b1c_obj], data='Tree 1, level 2, branch 1')
	t1l2b2_obj = putil.tree.TreeNode(name='t1l2b2', children=[t1l3b2a_obj, t1l3b2b_obj, t1l3b2c_obj], data='Tree 1, level 2, branch 2')
	#
	t1l1_obj = putil.tree.TreeNode(name='t1l1', children=[t1l2b1_obj, t1l2b2_obj], data='Tree 1, level 1')
	###
	t2l1_obj = putil.tree.TreeNode(name='t2l1', data='Tree 2, level 1')
	#
	t2l3b1a_obj = putil.tree.TreeNode(name='t2l3b1a', data='Tree 2, level 3, branch 1, child a')
	t2l3b1b_obj = putil.tree.TreeNode(name='t2l3b1b', data='Tree 2, level 3, branch 1, child b')
	t2l3b1c_obj = putil.tree.TreeNode(name='t2l3b1c', data='Tree 2, level 3, branch 1, child c')
	#
	t2l2b1_obj = putil.tree.TreeNode(name='t2l2b1', parent=t2l1_obj, children=[t2l3b1a_obj, t2l3b1b_obj, t2l3b1c_obj], data='Tree 2, level 2, branch 1')	#pylint: disable=W0612
	#
	t2l3b2a_obj = putil.tree.TreeNode(name='t2l3b2a', data='Tree 2, level 3, branch 2, child a')
	t2l3b2b_obj = putil.tree.TreeNode(name='t2l3b2b', data='Tree 2, level 3, branch 2, child b')
	t2l3b2c_obj = putil.tree.TreeNode(name='t2l3b2c', data='Tree 2, level 3, branch 2, child c')
	#
	t2l2b2_obj = putil.tree.TreeNode(name='t2l2b2', children=t2l3b2a_obj, data='Tree 2, level 2, branch 2')
	t2l2b2_obj.add_children([t2l3b2b_obj, t2l3b2c_obj])
	t2l2b2_obj.parent = t2l1_obj
	#
	t3l1_obj = putil.tree.TreeNode(name='t3l1', children=putil.tree.TreeNode(name='t3l2', data='Tree 2, level 2'), data='Tree 3, level 1')
	t3l1_obj.children = None

	return t1l1_obj, t2l1_obj, t3l1_obj


class TestTreeNode(object):	#pylint: disable=W0232
	""" Tests for CsvFile class """
	def test_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the node name is of the wrong type """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name=5)
		test_list.append(excinfo.value.message == 'Argument `name` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.tree.TreeNode(name='a.b. c')
		test_list.append(excinfo.value.message == 'Argument `name` is not a valid node name')
		# These statement should not raise any exception
		_ = putil.tree.TreeNode(name='a.b.c').name
		assert test_list == len(test_list)*[True]

	def test_children_error(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the node children is of the wrong type """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name='a', children=5)
		test_list.append(excinfo.value.message == 'Argument `children` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name='a', children=dict())
		test_list.append(excinfo.value.message == 'Argument `children` is of the wrong type')
		# These statement should not raise any exception
		test_list.append(putil.tree.TreeNode(name='a').children == None)
		_ = putil.tree.TreeNode(name='a', children=putil.tree.TreeNode(name='b'))
		_ = putil.tree.TreeNode(name='a', children=putil.tree.TreeNode(name='b'))
		_ = putil.tree.TreeNode(name='a', children=[putil.tree.TreeNode(name='b'), putil.tree.TreeNode(name='c')])
		#
		assert test_list == len(test_list)*[True]

	def test_children_and_children_names_work(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property children works as expected """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.children_names == ['t1l2b1', 't1l2b2'])
		test_list.append(tree2.children_names == ['t2l2b1', 't2l2b2'])
		test_list.append(tree1.children[0].children_names == ['t1l3b1a', 't1l3b1b', 't1l3b1c'])
		test_list.append(tree1.children[0].children[0].children_names == None)
		test_list.append(tree1.children[0].children[1].children_names == None)
		test_list.append(tree1.children[0].children[2].children_names == None)
		test_list.append(tree1.children[1].children_names == ['t1l3b2a', 't1l3b2b', 't1l3b2c'])
		test_list.append(tree1.children[1].children[0].children_names == None)
		test_list.append(tree1.children[1].children[1].children_names == None)
		test_list.append(tree1.children[1].children[2].children_names == None)
		test_list.append(tree2.children[0].children_names == ['t2l3b1a', 't2l3b1b', 't2l3b1c'])
		test_list.append(tree2.children[0].children[0].children_names == None)
		test_list.append(tree2.children[0].children[1].children_names == None)
		test_list.append(tree2.children[0].children[2].children_names == None)
		test_list.append(tree2.children[1].children_names == ['t2l3b2a', 't2l3b2b', 't2l3b2c'])
		test_list.append(tree2.children[1].children[0].children_names == None)
		test_list.append(tree2.children[1].children[1].children_names == None)
		test_list.append(tree2.children[1].children[2].children_names == None)
		test_list.append(tree3.children == None)
		#
		assert test_list == len(test_list)*[True]

	def test_add_children_error(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when add_children() method is given is of the wrong type """
		test_list = list()
		obj = putil.tree.TreeNode(name='a', children=putil.tree.TreeNode(name='b'))
		with pytest.raises(TypeError) as excinfo:
			obj.add_children(5)
		test_list.append(excinfo.value.message == 'Argument `children` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.add_children({})
		test_list.append(excinfo.value.message == 'Argument `children` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			obj.add_children(putil.tree.TreeNode(name='b'))
		test_list.append(excinfo.value.message == 'Node b is already a child of current node')
		with pytest.raises(ValueError) as excinfo:
			obj.add_children([putil.tree.TreeNode(name='c'), putil.tree.TreeNode(name='b')])
		test_list.append(excinfo.value.message == 'Node b is already a child of current node')
		#
		assert test_list == len(test_list)*[True]

	def test_add_children_works(self):	#pylint: disable=C0103,R0201
		""" Test that the method add_children() works as expected """
		test_list = list()
		obj = putil.tree.TreeNode(name='a', children=putil.tree.TreeNode(name='b'))
		#
		parent, children = obj.parent, obj.children
		obj.add_children(None)
		test_list.append((obj.parent, obj.children) == (parent, children))
		#
		obj.children = None
		test_list.append(obj.children == None)
		obj.add_children(None)
		test_list.append(obj.children == None)
		#
		obj.children = None
		test_list.append(obj.children == None)
		obj.add_children(putil.tree.TreeNode(name='b'))
		test_list.append(obj.children_names == ['b'])
		#
		obj.children = None
		test_list.append(obj.children == None)
		obj.add_children([putil.tree.TreeNode(name='b'), putil.tree.TreeNode(name='c')])
		test_list.append(obj.children_names == ['b', 'c'])
		#
		obj.children = putil.tree.TreeNode(name='b')
		test_list.append(obj.children_names == ['b'])
		obj.add_children(putil.tree.TreeNode(name='c'))
		test_list.append(obj.children_names == ['b', 'c'])
		#
		obj.children = putil.tree.TreeNode(name='b')
		test_list.append(obj.children_names == ['b'])
		obj.add_children([putil.tree.TreeNode(name='c'), putil.tree.TreeNode(name='d')])
		test_list.append(obj.children_names == ['b', 'c', 'd'])
		#
		assert test_list == len(test_list)*[True]

	def test_parent_error(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the node parent is of the wrong type """
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name='a', parent=5)
		test_list.append(excinfo.value.message == 'Argument `parent` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name='a', parent=dict())
		test_list.append(excinfo.value.message == 'Argument `parent` is of the wrong type')
		# These statement should not raise any exception
		test_list.append(putil.tree.TreeNode(name='a').parent == None)
		test_list.append(putil.tree.TreeNode(name='a', parent=putil.tree.TreeNode(name='b')).parent_name == 'b')
		#
		assert test_list == len(test_list)*[True]

	def test_parent_and_parent_name_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the properties parent and parent_name work as expected """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		#
		test_list.append(tree1.parent == None)
		test_list.append(tree1.parent_name == None)
		test_list.append(tree1.children[0].parent == tree1)
		test_list.append(tree1.children[0].parent_name == 't1l1')
		test_list.append(tree1.children[1].parent == tree1)
		test_list.append(tree1.children[1].parent_name == 't1l1')
		test_list.append(tree1.children[0].children[0].parent == tree1.children[0])
		test_list.append(tree1.children[0].children[0].parent_name == 't1l2b1')
		test_list.append(tree1.children[0].children[1].parent == tree1.children[0])
		test_list.append(tree1.children[0].children[1].parent_name == 't1l2b1')
		test_list.append(tree1.children[0].children[2].parent == tree1.children[0])
		test_list.append(tree1.children[0].children[2].parent_name == 't1l2b1')
		test_list.append(tree1.children[1].children[0].parent == tree1.children[1])
		test_list.append(tree1.children[1].children[0].parent_name == 't1l2b2')
		test_list.append(tree1.children[1].children[1].parent == tree1.children[1])
		test_list.append(tree1.children[1].children[1].parent_name == 't1l2b2')
		test_list.append(tree1.children[1].children[2].parent == tree1.children[1])
		test_list.append(tree1.children[1].children[2].parent_name == 't1l2b2')
		#
		test_list.append(tree2.parent == None)
		test_list.append(tree2.parent_name == None)
		test_list.append(tree2.children[0].parent == tree2)
		test_list.append(tree2.children[0].parent_name == 't2l1')
		test_list.append(tree2.children[1].parent == tree2)
		test_list.append(tree2.children[1].parent_name == 't2l1')
		test_list.append(tree2.children[0].children[0].parent == tree2.children[0])
		test_list.append(tree2.children[0].children[0].parent_name == 't2l2b1')
		test_list.append(tree2.children[0].children[1].parent == tree2.children[0])
		test_list.append(tree2.children[0].children[1].parent_name == 't2l2b1')
		test_list.append(tree2.children[0].children[2].parent == tree2.children[0])
		test_list.append(tree2.children[0].children[2].parent_name == 't2l2b1')
		test_list.append(tree2.children[1].children[0].parent == tree2.children[1])
		test_list.append(tree2.children[1].children[0].parent_name == 't2l2b2')
		test_list.append(tree2.children[1].children[1].parent == tree2.children[1])
		test_list.append(tree2.children[1].children[1].parent_name == 't2l2b2')
		test_list.append(tree2.children[1].children[2].parent == tree2.children[1])
		test_list.append(tree2.children[1].children[2].parent_name == 't2l2b2')
		#
		test_list.append(tree3.parent == None)
		test_list.append(tree3.parent_name == None)
		#
		assert test_list == len(test_list)*[True]

	def test_data_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property data works as expected """
		tree1, _, _ = default_trees
		test_list = list()
		#
		test_list.append(tree1.data == 'Tree 1, level 1')
		test_list.append(tree1.children[0].data == 'Tree 1, level 2, branch 1')
		test_list.append(tree1.children[1].children[2].data == 'Tree 1, level 3, branch 2, child c')
		tree1.children[1].children[2].data = None
		test_list.append(tree1.children[1].children[2].data == None)
		tree1.children[1].children[0].data = [5, 5, 2]
		test_list.append(tree1.children[1].children[0].data == [5, 5, 2])
		#
		assert test_list == len(test_list)*[True]

	def test_add_data_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the method add_data() works as expected """
		tree1, _, _ = default_trees
		test_list = list()
		#
		test_list.append(tree1.data == 'Tree 1, level 1')
		tree1.add_data(5)
		test_list.append(tree1.data == ['Tree 1, level 1', 5])
		obj = tree1.children[1]
		test_list.append(obj.data == 'Tree 1, level 2, branch 2')
		obj.data = None
		test_list.append(obj.data == None)
		obj.add_data('Hello')
		test_list.append(obj.data == 'Hello')
		obj.add_data('world!')
		test_list.append(obj.data == ['Hello', 'world!'])
		#
		assert test_list == len(test_list)*[True]

	def test_str(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the method __str__ works as expected """
		tree1, tree2, tree3 = default_trees
		obj = putil.tree.TreeNode(name='dtree', children=putil.tree.TreeNode(name='my_child', data='Tree 2, level 2'))
		test_list = list()
		#
		test_list.append(str(tree1) == 'Name: t1l1\nParent: None\nChildren: t1l2b1, t1l2b2\nData: Tree 1, level 1')
		tree2.children[0].children[1].add_data(14.3)
		test_list.append(str(tree2.children[0].children[1]) == "Name: t2l3b1b\nParent: t2l2b1\nChildren: None\nData: ['Tree 2, level 3, branch 1, child b', 14.3]")
		test_list.append(str(tree3) == 'Name: t3l1\nParent: None\nChildren: None\nData: Tree 3, level 1')
		test_list.append(str(obj) == 'Name: dtree\nParent: None\nChildren: my_child\nData: None')
		#
		assert test_list == len(test_list)*[True]

	def test_is_root(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property is_root works as expected """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.is_root == True)
		test_list.append(tree2.children[0].is_root == False)
		test_list.append(tree2.children[0].children[2].is_root == False)
		test_list.append(tree3.is_root == True)
		assert test_list == len(test_list)*[True]

	def test_is_leaf(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the property is_leaf works as expected """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.is_leaf == False)
		test_list.append(tree2.children[0].is_leaf == False)
		test_list.append(tree2.children[0].children[2].is_leaf == True)
		test_list.append(tree3.is_leaf == True)
		assert test_list == len(test_list)*[True]

	def test_cannot_delete_attributes(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _ = default_trees
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del tree1.children
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.children_names
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.is_leaf
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.is_root
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.data
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.name
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.parent
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del tree1.parent_name
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
