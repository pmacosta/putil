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
	t1l3b1a_obj = putil.tree.TreeNode(name='t1l3b1a', data='Tree 1, Level 3, branch 1, child a')
	t1l3b1b_obj = putil.tree.TreeNode(name='t1l3b1b', data='Tree 1, Level 3, branch 1, child b')
	t1l3b1c_obj = putil.tree.TreeNode(name='t1l3b1c', data='Tree 1, Level 3, branch 1, child c')
	#
	t1l3b2a_obj = putil.tree.TreeNode(name='t1l3b2a', data='Tree 1, Level 3, branch 2, child a')
	t1l3b2b_obj = putil.tree.TreeNode(name='t1l3b2b', data='Tree 1, Level 3, branch 2, child b')
	t1l3b2c_obj = putil.tree.TreeNode(name='t1l3b2c', data='Tree 1, Level 3, branch 2, child c')
	#
	t1l2b1_obj = putil.tree.TreeNode(name='t1l2b1', children=[t1l3b1a_obj, t1l3b1b_obj, t1l3b1c_obj], data='Tree 1, Level 2, branch 1')
	t1l2b2_obj = putil.tree.TreeNode(name='t1l2b2', children=[t1l3b2a_obj, t1l3b2b_obj, t1l3b2c_obj], data='Tree 1, Level 2, branch 2')
	#
	t1l1_obj = putil.tree.TreeNode(name='t1l1', children=[t1l2b1_obj, t1l2b2_obj], data='Tree 1, Level 1')
	###
	t2l1_obj = putil.tree.TreeNode(name='t2l1', data='Tree 2, Level 1')
	#
	t2l3b1a_obj = putil.tree.TreeNode(name='t2l3b1a', data='Tree 2, Level 3, branch 1, child a')
	t2l3b1b_obj = putil.tree.TreeNode(name='t2l3b1b', data='Tree 2, Level 3, branch 1, child b')
	t2l3b1c_obj = putil.tree.TreeNode(name='t2l3b1c', data='Tree 2, Level 3, branch 1, child c')
	#
	t2l2b1_obj = putil.tree.TreeNode(name='t2l2b1', parent=t2l1_obj, children=[t2l3b1a_obj, t2l3b1b_obj, t2l3b1c_obj], data='Tree 2, Level 2, branch 1')	#pylint: disable=W0612
	#
	t2l3b2a_obj = putil.tree.TreeNode(name='t2l3b2a', data='Tree 2, Level 3, branch 2, child a')
	t2l3b2b_obj = putil.tree.TreeNode(name='t2l3b2b', data='Tree 2, Level 3, branch 2, child b')
	t2l3b2c_obj = putil.tree.TreeNode(name='t2l3b2c', data='Tree 2, Level 3, branch 2, child c')
	#
	t2l2b2_obj = putil.tree.TreeNode(name='t2l2b2', children=t2l3b2a_obj, data='Tree 2, Level 2, branch 2')
	t2l2b2_obj.add_children([t2l3b2b_obj, t2l3b2c_obj])
	t2l2b2_obj.parent = t2l1_obj
	#
	t3l1_obj = putil.tree.TreeNode(name='t3l1', children=putil.tree.TreeNode(name='t3l2', data='Tree 2, Level 2'), data='Tree 2, Level 1')
	t3l1_obj.children = None

	return t1l1_obj, t2l1_obj, t3l1_obj


class TestTreeNode(object):	#pylint: disable=W0232
	""" Tests for CsvFile class """
	def test_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the node name is of the wrong type """
		with pytest.raises(TypeError) as excinfo:
			putil.tree.TreeNode(name=5)
		# These statement should not raise any exception
		_ = putil.tree.TreeNode(name='a').name
		assert excinfo.value.message == 'Argument `name` is of the wrong type'

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
		assert test_list == 3*[True]

	def test_children_works(self, default_trees):	#pylint: disable=C0103,R0201,W0621
		""" Test that the method children() works as expected """
		tree1, tree2, tree3 = default_trees
		test_list = list()
		test_list.append(tree1.children_names == ['t1l2b1', 't1l2b2'])
		test_list.append(tree2.children_names == ['t2l2b1', 't2l2b2'])
		test_list.append(tree1.children[0].children_names == ['t1l3b1a', 't1l3b1b', 't1l3b1c'])
		test_list.append(tree1.children[1].children_names == ['t1l3b2a', 't1l3b2b', 't1l3b2c'])
		test_list.append(tree2.children[0].children_names == ['t2l3b1a', 't2l3b1b', 't2l3b1c'])
		test_list.append(tree2.children[1].children_names == ['t2l3b2a', 't2l3b2b', 't2l3b2c'])
		test_list.append(tree3.children == None)
		assert test_list == 7*[True]

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
		assert test_list == 4*[True]

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
		assert test_list == 11*[True]
