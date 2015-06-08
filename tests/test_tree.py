# -*- coding: utf-8 -*-
# test_tree.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,R0904,R0914,W0212,W0232,W0621

import copy
import pytest

import putil.test
import putil.tree


###
# Fixtures
###
@pytest.fixture
def default_trees():
	"""
	Provides a default tree to be used in testing the
	putil.tree.TreeNode() class
	"""
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
	t1obj.add_nodes({'name':'t1l1', 'data':'Tree 1, level 1'})
	t1obj.add_nodes([
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
	t2obj.add_nodes(
		{'name':'t2l1.t2l2b1.t2l3b1a', 'data':'Tree 2, level 3, branch 1, child a'}
	)
	t2obj.add_nodes(
		{'name':'t2l1.t2l2b1.t2l3b1b', 'data':'Tree 2, level 3, branch 1, child b'}
	)
	t2obj.add_nodes(
		{'name':'t2l1.t2l2b1.t2l3b1c', 'data':'Tree 2, level 3, branch 1, child c'}
	)
	#
	t2obj.add_nodes({'name':'t2l1', 'data':'Tree 2, level 1'})
	#
	t2obj.add_nodes({'name':'t2l1.t2l2b1', 'data':'Tree 2, level 2, branch 1'})
	#
	t2obj.add_nodes([
		{'name':'t2l1.t2l2b2.t2l3b2a', 'data':'Tree 2, level 3, branch 2, child a'},
		{'name':'t2l1.t2l2b2.t2l3b2b', 'data':'Tree 2, level 3, branch 2, child b'},
		{'name':'t2l1.t2l2b2.t2l3b2c', 'data':'Tree 2, level 3, branch 2, child c'},
	])
	#
	t2obj.add_nodes({'name':'t2l1.t2l2b2', 'data':'Tree 2, level 2, branch 2'})
	#
	t3obj = putil.tree.Tree()
	t3obj.add_nodes([
		{'name':'t3l1', 'data':'Tree 3, level 1'},
		{'name':'t3l1.t3l2', 'data':'Tree 2, level 2'}
	])
	t3obj.delete_subtree('t3l1.t3l2')

	t4obj = putil.tree.Tree()
	t4obj.add_nodes([
		{'name':'root.branch1', 'data':5},
		{'name':'root.branch1', 'data':7},
		{'name':'root.branch2', 'data':list()},
		{'name':'root.branch1.leaf1', 'data':list()},
		{'name':'root.branch1.leaf1.subleaf1', 'data':333},
		{'name':'root.branch1.leaf2', 'data':'Hello world!'},
		{'name':'root.branch1.leaf2.subleaf2', 'data':list()},
	])

	return t1obj, t2obj, t3obj, t4obj


###
# Tests
###
class TestTreeNode(object):
	""" Tests for CsvFile class """

	def test_node_names(self):
		""" Test for node_names custom PyContract contract """
		obj = putil.tree.Tree()
		putil.test.assert_exception(
			obj._validate_nodes_with_data,
			{'names':3},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			obj._validate_nodes_with_data,
			{'names':[{'name', 'hello'}, {'name':5, 'data':'a'}],},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			obj._validate_nodes_with_data,
			{'names':{'name':5, 'data':'a'}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			obj._validate_nodes_with_data,
			{'names':{'name':'a. b', 'data':None}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			obj._validate_nodes_with_data,
			{'names':{'name':'a.b..c', 'data':1.0}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		obj._validate_nodes_with_data({'name':'a.b.c', 'data':'a'})
		obj._validate_nodes_with_data([
			{'name':'a.b', 'data':3},
			{'name':'a.b.c', 'data':'a'}
		])

	def test_node_separator_errors(self):
		""" Check that validation for node_separator argument works as expected """
		putil.test.assert_exception(
			putil.tree.Tree,
			{'node_separator':3},
			RuntimeError,
			'Argument `node_separator` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree,
			{'node_separator':'hello'},
			RuntimeError,
			'Argument `node_separator` is not valid'
		)
		putil.tree.Tree('+')

	def test_node_separator_works(self):
		""" Check that the node separator feature works as expected """
		def create_tree():
			""" Create test tree """
			tobj = putil.tree.Tree('+')
			tobj.add_nodes([
				{'name':'root+branch1', 'data':5},
				{'name':'root+branch1', 'data':7},
				{'name':'root+branch2', 'data':list()},
				{'name':'root+branch1+leaf1', 'data':list()},
				{'name':'root+branch1+leaf1+subleaf1', 'data':333},
				{'name':'root+branch1+leaf2', 'data':'Hello world!'},
				{'name':'root+branch1+leaf2+subleaf2', 'data':list()},
			])
			return tobj
		tobj = create_tree()
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf1\n'
							 '││└subleaf1 (*)\n'
							 '│└leaf2 (*)\n'
							 '│ └subleaf2\n'
							 '└branch2')
		tobj.collapse_subtree('root+branch1')
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf1+subleaf1 (*)\n'
						     '│└leaf2 (*)\n'
						     '│ └subleaf2\n'
						     '└branch2')
		tobj = create_tree()
		tobj.copy_subtree('root+branch1', 'root+branch3')
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf1\n'
						     '││└subleaf1 (*)\n'
						     '│└leaf2 (*)\n'
						     '│ └subleaf2\n'
						     '├branch2\n'
						     '└branch3 (*)\n'
						     ' ├leaf1\n'
						     ' │└subleaf1 (*)\n'
						     ' └leaf2 (*)\n'
						     '  └subleaf2')
		tobj = create_tree()
		tobj.delete_subtree(['root+branch1+leaf1', 'root+branch2'])
		assert str(tobj) == ('root\n'
							 '└branch1 (*)\n'
							 ' └leaf2 (*)\n'
							 '  └subleaf2')
		tobj = create_tree()
		tobj.add_nodes([{'name':'root+branch1+leaf1+subleaf2', 'data':list()},
			{'name':'root+branch2+leaf1', 'data':'loren ipsum'},
			{'name':'root+branch2+leaf1+another_subleaf1', 'data':list()},
			{'name':'root+branch2+leaf1+another_subleaf2', 'data':list()}
		])
		tobj.flatten_subtree('root+branch1+leaf1')
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf1+subleaf1 (*)\n'
							 '│├leaf1+subleaf2\n'
							 '│└leaf2 (*)\n'
							 '│ └subleaf2\n'
							 '└branch2\n'
							 ' └leaf1 (*)\n'
							 '  ├another_subleaf1\n'
							 '  └another_subleaf2')
		tobj.flatten_subtree('root+branch2+leaf1')
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf1+subleaf1 (*)\n'
							 '│├leaf1+subleaf2\n'
							 '│└leaf2 (*)\n'
							 '│ └subleaf2\n'
							 '└branch2\n'
							 ' └leaf1 (*)\n'
							 '  ├another_subleaf1\n'
							 '  └another_subleaf2')
		tobj = create_tree()
		assert sorted(tobj.get_subtree('root+branch1')) == sorted([
			'root+branch1',
			'root+branch1+leaf1',
			'root+branch1+leaf1+subleaf1',
			'root+branch1+leaf2',
			'root+branch1+leaf2+subleaf2'
		])
		tobj = create_tree()
		tobj.make_root('root+branch1')
		assert str(tobj) == ('root+branch1 (*)\n'
							 '├leaf1\n'
							 '│└subleaf1 (*)\n'
							 '└leaf2 (*)\n'
							 ' └subleaf2')
		tobj = create_tree()
		tobj.rename_node('root+branch1+leaf1', 'root+branch1+mapleleaf1')
		assert str(tobj) == ('root\n'
							 '├branch1 (*)\n'
							 '│├leaf2 (*)\n'
							 '││└subleaf2\n'
							 '│└mapleleaf1\n'
							 '│ └subleaf1 (*)\n'
							 '└branch2')

	def test_errors_for_single_node_function(self):
		"""
		Check that correct exceptions are raise for methods that have a single
		NodeName argument that has to be in the tree
		"""
		obj = putil.tree.Tree()
		method_list = [
			'collapse_subtree', 'flatten_subtree', 'get_children', 'get_data',
			'get_leafs', 'get_node', 'get_node_children', 'get_node_parent',
			'get_subtree', 'is_leaf', 'is_root', 'is_leaf', 'make_root',
			'print_node'
		]
		for method in method_list:
			putil.test.assert_exception(
				getattr(obj, method),
				{'name':5},
				RuntimeError,
				'Argument `name` is not valid'
			)
			putil.test.assert_exception(
				getattr(obj, method),
				{'name':'a.b..c'},
				RuntimeError,
				'Argument `name` is not valid'
			)
			putil.test.assert_exception(
				getattr(obj, method),
				{'name':'a.b.c'},
				RuntimeError,
				'Node a.b.c not in tree'
			)

	def test_add_nodes_errors(self):
		""" Test that add() method raises the right exceptions """
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':5},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':{'key':'a'}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':{'name':'a'}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':{'data':'a'}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':{'name':'a.b', 'data':'a', 'edata':5}},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[{'name':'a.c', 'data':'a'}, {'key':'a'}]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[{'name':'a.c', 'data':'a'}, {'name':'a'}]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[{'name':'a.c', 'data':'a'}, {'data':'a'}]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[
				{'name':'a.c', 'data':'a'},
				{'name':'a.b', 'data':'a', 'edata':5}
			]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		#putil.test.assert_exception(
		#	putil.tree.Tree().add_nodes,
		#	{'nodes':[{'name':'a.c', 'data':'a'}, {'name':'d.e', 'data':'a'}]},
		#	RuntimeError,
		#	'Argument `nodes` is not valid'
		#)
		putil.test.assert_exception(
			putil.tree.Tree().add_nodes,
			{'nodes':[{'name':'a.c', 'data':'a'}, {'name':'d.e', 'data':'a'}]},
			ValueError,
			'Illegal node name: d.e'
		)

	def test_add_nodes_works(self, default_trees):
		""" Test that add() method works """
		tree1, tree2, tree3, _ = default_trees
		assert tree1.get_children('t1l1') == ['t1l1.t1l2b1', 't1l1.t1l2b2']
		assert tree1.get_children('t1l1.t1l2b1') == [
			't1l1.t1l2b1.t1l3b1a',
			't1l1.t1l2b1.t1l3b1b',
			't1l1.t1l2b1.t1l3b1c'
		]
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1a') == list()
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1b') == list()
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1c') == list()
		assert tree1.get_children('t1l1.t1l2b2') == [
			't1l1.t1l2b2.t1l3b2a',
			't1l1.t1l2b2.t1l3b2b',
			't1l1.t1l2b2.t1l3b2c'
		]
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2a') == list()
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2b') == list()
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2c') == list()
		assert tree2.get_children('t2l1') == ['t2l1.t2l2b1', 't2l1.t2l2b2']
		assert tree2.get_children('t2l1.t2l2b1') == [
			't2l1.t2l2b1.t2l3b1a',
			't2l1.t2l2b1.t2l3b1b',
			't2l1.t2l2b1.t2l3b1c'
		]
		assert tree2.get_children('t2l1.t2l2b1.t2l3b1a') == list()
		assert tree2.get_children('t2l1.t2l2b1.t2l3b1b') == list()
		assert tree2.get_children('t2l1.t2l2b1.t2l3b1c') == list()
		assert tree2.get_children('t2l1.t2l2b2') == [
			't2l1.t2l2b2.t2l3b2a',
			't2l1.t2l2b2.t2l3b2b',
			't2l1.t2l2b2.t2l3b2c'
		]
		assert tree2.get_children('t2l1.t2l2b2.t2l3b2a') == list()
		assert tree2.get_children('t2l1.t2l2b2.t2l3b2b') == list()
		assert tree2.get_children('t2l1.t2l2b2.t2l3b2c') == list()
		assert tree3.get_children('t3l1') == list()
		# Test that data id's are different
		tree4 = putil.tree.Tree()
		ndata = [1, 2, 3]
		tree4.add_nodes([
			{'name':'root', 'data':list()},
			{'name':'root.leaf1', 'data':ndata},
			{'name':'root.leaf2', 'data':ndata}
		])
		assert id(tree4.get_data('root.leaf1')) != id(tree4.get_data('root.leaf2'))

	def test_collapse_works(self):
		""" Test that collapse method works """
		def create_tree():
			""" Create auxiliary tree for testing of recursive argument """
			tobj = putil.tree.Tree('/')
			tobj.add_nodes([
				{'name':'hello/world/root', 'data':list()},
			    {'name':'hello/world/root/anode', 'data':7},
			    {'name':'hello/world/root/bnode', 'data':list()},
			    {'name':'hello/world/root/cnode', 'data':list()},
        	    {'name':'hello/world/root/bnode/anode', 'data':list()},
        	    {'name':'hello/world/root/cnode/anode/leaf', 'data':list()}
        	])
			return tobj
		t1obj = putil.tree.Tree()
		t1obj.add_nodes([
			{'name':'l0.l1', 'data':'hello'},
			{'name':'l0.l1.l2.l3b2.l4b2b1', 'data':5},
			{'name':'l0.l1.l2.l3b2.l4b2b1.l5b2b1b1', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b1', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l4b1b1.l5b1b1b1.l6b1b1b1b2', 'data':list()},
			{'name':'l0.l1.l2.l3b1.l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1', 'data':[]},
		])
		putil.test.assert_exception(
			t1obj.collapse_subtree,
			{'name':t1obj.root_name, 'recursive':5},
			RuntimeError,
			'Argument `recursive` is not valid'
		)
		# Original tree       Collapsed tree
		# l0                  l0.l1 (*)
		# └l1 (*)             └l2
		#  └l2                 ├l3b1
		#   ├l3b1              │├l4b1b1.l5b1b1b1
		#   │├l4b1b1           ││├l6b1b1b1b1
		#   ││└l5b1b1b1        ││└l6b1b1b1b2
		#   ││ ├l6b1b1b1b1     │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1
		#   ││ └l6b1b1b1b2     └l3b2.l4b2b1 (*)
		#   │└l5b1b1            └l5b2b1b1
		#   │ └l5b1b1b2
		#   │  └l6b1b1b2b1
		#   │   └l7b1b1b2b1b1
		#   └l3b2
		#    └l4b2b1 (*)
		#     └l5b2b1b1
		t1obj.collapse_subtree(t1obj.root_name)
		assert str(t1obj) == ('l0.l1 (*)\n'
							  '└l2\n'
							  ' ├l3b1\n'
							  ' │├l4b1b1.l5b1b1b1\n'
							  ' ││├l6b1b1b1b1\n'
							  ' ││└l6b1b1b1b2\n'
							  ' │└l5b1b1.l5b1b1b2.l6b1b1b2b1.l7b1b1b2b1b1\n'
							  ' └l3b2.l4b2b1 (*)\n'
							  '  └l5b2b1b1')
		assert t1obj.get_data('l0.l1') == ['hello']
		assert t1obj.get_data('l0.l1.l2.l3b2.l4b2b1') == [5]
		tobj = create_tree()
		tobj.collapse_subtree(tobj.root_name, False)
		assert str(tobj) == ('hello/world/root\n'
							 '├anode (*)\n'
							 '├bnode\n'
							 '│└anode\n'
							 '└cnode\n'
							 ' └anode\n'
							 '  └leaf')
		tobj = create_tree()
		tobj.collapse_subtree(tobj.root_name, True)
		assert str(tobj) == ('hello/world/root\n'
							 '├anode (*)\n'
							 '├bnode/anode\n'
							 '└cnode/anode/leaf')

	def test_copy_subtree_errors(self):
		""" Test that copy_subtree() method raises the right exceptions """
		obj = putil.tree.Tree()
		obj.add_nodes([
			{'name':'root', 'data':list()},
			{'name':'root.leaf1', 'data':5},
			{'name':'root.leaf2', 'data':7}
		])
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':5, 'dest_node':'root.x'},
			RuntimeError,
			'Argument `source_node` is not valid'
		)
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':'.x.y', 'dest_node':'root.x'},
			RuntimeError,
			'Argument `source_node` is not valid'
		)
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':'hello', 'dest_node':'root.x'},
			RuntimeError,
			'Node hello not in tree'
		)
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':'root.leaf1', 'dest_node':5},
			RuntimeError,
			'Argument `dest_node` is not valid'
		)
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':'root.leaf1', 'dest_node':'x..y'},
			RuntimeError,
			'Argument `dest_node` is not valid'
		)
		putil.test.assert_exception(
			obj.copy_subtree,
			{'source_node':'root.leaf1', 'dest_node':'teto.leaf2'},
			RuntimeError,
			'Illegal root in destination node'
		)

	def test_copy_subtree_works(self, default_trees):
		""" Test that copy_subtree() method works """
		_, _, _, tree4 = default_trees
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
		assert str(tree4) == ('root\n'
							  '├branch1 (*)\n'
							  '│├leaf1\n'
							  '││└subleaf1 (*)\n'
							  '│└leaf2 (*)\n'
							  '│ └subleaf2\n'
							  '└branch2\n'
							  ' └branch3 (*)\n'
							  '  ├leaf1\n'
							  '  │└subleaf1 (*)\n'
							  '  └leaf2 (*)\n'
							  '   └subleaf2')
		# Test that there are no pointers between source and destination data
		assert (id(tree4.get_data('root.branch1')) !=
			   id(tree4.get_data('root.branch2.branch3')))
		assert (id(tree4.get_data('root.branch1.leaf1')) !=
			   id(tree4.get_data('root.branch2.branch3.leaf1')))
		assert (id(tree4.get_data('root.branch1.leaf1.subleaf1')) !=
			   id(tree4.get_data('root.branch2.branch3.leaf1.subleaf1')))
		assert (id(tree4.get_data('root.branch1.leaf2')) !=
			   id(tree4.get_data('root.branch2.branch3.leaf2')))
		assert (id(tree4.get_data('root.branch1.leaf2.subleaf2')) !=
			   id(tree4.get_data('root.branch2.branch3.leaf2.subleaf2')))
		# Test that data values are the same
		assert (tree4.get_data('root.branch1') ==
			   tree4.get_data('root.branch2.branch3'))
		assert (tree4.get_data('root.branch1.leaf1') ==
			   tree4.get_data('root.branch2.branch3.leaf1'))
		assert (tree4.get_data('root.branch1.leaf1.subleaf1') ==
			   tree4.get_data('root.branch2.branch3.leaf1.subleaf1'))
		assert (tree4.get_data('root.branch1.leaf2') ==
			   tree4.get_data('root.branch2.branch3.leaf2'))
		assert (tree4.get_data('root.branch1.leaf2.subleaf2') ==
			   tree4.get_data('root.branch2.branch3.leaf2.subleaf2'))

	def test_delete_errors(self, default_trees):
		""" Test that delete() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':'a..b'},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':['t1l1', 'a..b']},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':5},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':['t1l1', 5]},
			RuntimeError,
			'Argument `nodes` is not valid'
		)
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':'a.b.c'},
			RuntimeError,
			'Node a.b.c not in tree'
		)
		putil.test.assert_exception(
			tree1.delete_subtree,
			{'nodes':['t1l1', 'a.b.c']},
			RuntimeError,
			'Node a.b.c not in tree'
		)

	def test_delete_works(self, default_trees):
		""" Test that delete() method works """
		tree1, tree2, _, _ = default_trees
		tree1.delete_subtree('t1l1.t1l2b2')
		tree1.delete_subtree('t1l1.t1l2b1.t1l3b1b')
		tree2.delete_subtree('t2l1')
		assert str(tree1) == ('t1l1 (*)\n'
							  '└t1l2b1 (*)\n'
							  ' ├t1l3b1a (*)\n'
							  ' └t1l3b1c (*)')
		assert str(tree2) == ''
		assert tree2.root_name is None
		tree2.add_nodes([
			{'name':'root.branch1', 'data':list()},
			{'name':'root.branch1.x', 'data':1999}
		])
		assert tree2.root_name == 'root'

	def test_flatten_subtree_works(self, default_trees):
		""" Test that flatten_subtree method works """
		_, _, _, tree4 = default_trees
		tree4.add_nodes([
			{'name':'root.branch1.leaf1.subleaf2', 'data':list()},
		    {'name':'root.branch2.leaf1', 'data':'loren ipsum'},
		    {'name':'root.branch2.leaf1.another_subleaf1', 'data':list()},
		    {'name':'root.branch2.leaf1.another_subleaf2', 'data':list()}
		])
		odata = copy.deepcopy(tree4.get_data('root.branch1.leaf1.subleaf1'))
		tree4.flatten_subtree('root.branch1.leaf1')
		assert str(tree4) == ('root\n'
							  '├branch1 (*)\n'
							  '│├leaf1.subleaf1 (*)\n'
							  '│├leaf1.subleaf2\n'
							  '│└leaf2 (*)\n'
							  '│ └subleaf2\n'
							  '└branch2\n'
							  ' └leaf1 (*)\n'
							  '  ├another_subleaf1\n'
							  '  └another_subleaf2')
		assert tree4.get_data('root.branch1.leaf1.subleaf1') == odata
		tree4.flatten_subtree('root.branch2.leaf1')
		assert str(tree4) == ('root\n'
							  '├branch1 (*)\n'
							  '│├leaf1.subleaf1 (*)\n'
							  '│├leaf1.subleaf2\n'
							  '│└leaf2 (*)\n'
							  '│ └subleaf2\n'
							  '└branch2\n'
							  ' └leaf1 (*)\n'
							  '  ├another_subleaf1\n'
							  '  └another_subleaf2')

	def test_get_children_works(self, default_trees):
		""" Test that get_children() method works """
		tree1, _, _, _ = default_trees
		assert tree1.get_children('t1l1') == ['t1l1.t1l2b1', 't1l1.t1l2b2']
		assert tree1.get_children('t1l1.t1l2b1') == [
			't1l1.t1l2b1.t1l3b1a',
			't1l1.t1l2b1.t1l3b1b',
			't1l1.t1l2b1.t1l3b1c'
		]
		assert tree1.get_children('t1l1.t1l2b2') == [
			't1l1.t1l2b2.t1l3b2a',
			't1l1.t1l2b2.t1l3b2b',
			't1l1.t1l2b2.t1l3b2c'
		]
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1a') == list()
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1b') == list()
		assert tree1.get_children('t1l1.t1l2b1.t1l3b1c') == list()
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2a') == list()
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2b') == list()
		assert tree1.get_children('t1l1.t1l2b2.t1l3b2c') == list()

	def test_get_data_works(self, default_trees):
		""" Test that get_data() method works """
		tree1, tree2, tree3, _ = default_trees
		assert tree1.get_data('t1l1') == ['Tree 1, level 1']
		assert tree1.get_data('t1l1.t1l2b1') == ['Tree 1, level 2, branch 1']
		assert tree1.get_data('t1l1.t1l2b1.t1l3b1a') == [
			'Tree 1, level 3, branch 1, child a'
		]
		assert tree1.get_data('t1l1.t1l2b1.t1l3b1b') == [
			'Tree 1, level 3, branch 1, child b'
		]
		assert tree1.get_data('t1l1.t1l2b1.t1l3b1c') == [
			'Tree 1, level 3, branch 1, child c']
		assert tree1.get_data('t1l1.t1l2b2') == ['Tree 1, level 2, branch 2'
										   ]
		assert tree1.get_data('t1l1.t1l2b2.t1l3b2a') == [
			'Tree 1, level 3, branch 2, child a']
		assert tree1.get_data('t1l1.t1l2b2.t1l3b2b') == [
			'Tree 1, level 3, branch 2, child b'
		]
		assert tree1.get_data('t1l1.t1l2b2.t1l3b2c') == [
			'Tree 1, level 3, branch 2, child c'
		]
		assert tree2.get_data('t2l1') == ['Tree 2, level 1']
		assert tree2.get_data('t2l1.t2l2b1') == ['Tree 2, level 2, branch 1']
		assert tree2.get_data('t2l1.t2l2b1.t2l3b1a') == [
			'Tree 2, level 3, branch 1, child a'
		]
		assert tree2.get_data('t2l1.t2l2b1.t2l3b1b') == [
			'Tree 2, level 3, branch 1, child b'
		]
		assert tree2.get_data('t2l1.t2l2b1.t2l3b1c') == [
			'Tree 2, level 3, branch 1, child c']
		assert tree2.get_data('t2l1.t2l2b2') == ['Tree 2, level 2, branch 2'
										   ]
		assert tree2.get_data('t2l1.t2l2b2.t2l3b2a') == [
			'Tree 2, level 3, branch 2, child a'
		]
		assert tree2.get_data('t2l1.t2l2b2.t2l3b2b') == [
			'Tree 2, level 3, branch 2, child b'
		]
		assert tree2.get_data('t2l1.t2l2b2.t2l3b2c') == [
			'Tree 2, level 3, branch 2, child c'
		]
		assert tree3.get_data('t3l1') == ['Tree 3, level 1']
		tree4 = putil.tree.Tree()
		tree4.add_nodes({'name':'t4l1', 'data':list()})
		assert tree4.get_data('t4l1') == list()
		tree4.add_nodes([
			{'name':'t4l1', 'data':'Hello'},
			{'name':'t4l1', 'data':'world'}
		])
		tree4.add_nodes({'name':'t4l1', 'data':'!'})
		assert tree4.get_data('t4l1') == ['Hello', 'world', '!']

	def test_get_leafs_works(self, default_trees):
		""" Test that get_data() method works """
		tree1, tree2, tree3, tree4 = default_trees
		assert tree1.get_leafs('t1l1') == [
			't1l1.t1l2b1.t1l3b1a',
			't1l1.t1l2b1.t1l3b1b',
			't1l1.t1l2b1.t1l3b1c',
			't1l1.t1l2b2.t1l3b2a',
			't1l1.t1l2b2.t1l3b2b',
			't1l1.t1l2b2.t1l3b2c'
		]
		assert tree2.get_leafs('t2l1.t2l2b2') == [
			't2l1.t2l2b2.t2l3b2a',
			't2l1.t2l2b2.t2l3b2b',
			't2l1.t2l2b2.t2l3b2c'
		]
		assert tree3.get_leafs('t3l1') == ['t3l1']
		assert tree4.get_leafs('root.branch1.leaf2') == [
			'root.branch1.leaf2.subleaf2'
		]

	def test_get_node_works(self, default_trees):
		""" Test that get_node() method works """
		tree1, _, _, _ = default_trees
		assert tree1.get_node('t1l1') == {
			'parent':'',
			'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
			'data':['Tree 1, level 1']
		}
		assert tree1.get_node('t1l1.t1l2b1') == {
			'parent':'t1l1',
			'children':[
				't1l1.t1l2b1.t1l3b1a',
				't1l1.t1l2b1.t1l3b1b',
				't1l1.t1l2b1.t1l3b1c'
			],
			'data':['Tree 1, level 2, branch 1']
		}
		assert tree1.get_node('t1l1.t1l2b1.t1l3b1a') == {
			'parent':'t1l1.t1l2b1',
			'children':list(),
			'data':['Tree 1, level 3, branch 1, child a']
		}

	def test_get_node_children_works(self, default_trees):
		""" Test that get_node_children() method works """
		tree1, _, tree3, tree4 = default_trees
		assert tree1.get_node_children('t1l1') == [
			{
				'parent':'t1l1',
				'children':[
					't1l1.t1l2b1.t1l3b1a',
					't1l1.t1l2b1.t1l3b1b',
					't1l1.t1l2b1.t1l3b1c'
				],
				'data':['Tree 1, level 2, branch 1']
			},
			{
				'parent':'t1l1',
				'children':[
					't1l1.t1l2b2.t1l3b2a',
					't1l1.t1l2b2.t1l3b2b',
					't1l1.t1l2b2.t1l3b2c'
				],
				'data':['Tree 1, level 2, branch 2']
			}
		]
		assert tree3.get_node_children('t3l1') == list()
		assert tree4.get_node_children('root.branch1.leaf2') == [
			{'parent':'root.branch1.leaf2', 'children':[], 'data':[]}
		]

	def test_get_subtree_works(self, default_trees):
		""" Test that get_subtree() method works """
		_, _, tree3, tree4 = default_trees
		assert tree4.get_subtree('root.branch1') == [
			'root.branch1',
			'root.branch1.leaf1',
			'root.branch1.leaf1.subleaf1',
			'root.branch1.leaf2',
			'root.branch1.leaf2.subleaf2'
		]
		assert tree3.get_subtree('t3l1') == ['t3l1']

	def test_is_root(self, default_trees):
		""" Test that the property is_root works as expected """
		tree1, tree2, tree3, _ = default_trees
		assert tree1.is_root('t1l1')
		assert not tree2.is_root('t2l1.t2l2b1')
		assert not tree2.is_root('t2l1.t2l2b1.t2l3b1b')
		assert tree3.is_root('t3l1')

	def test_in_tree_errors(self, default_trees):
		""" Test that in_tree() method raises the right exceptions """
		tree1, _, _, _ = default_trees
		putil.test.assert_exception(
			tree1.in_tree,
			{'name':'a..b'},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tree1.in_tree,
			{'name':5},
			RuntimeError,
			'Argument `name` is not valid'
		)

	def test_in_tree_works(self, default_trees):
		""" Test that in_tree() method works """
		tree1, _, _, _ = default_trees
		assert not tree1.in_tree('x.x.x')
		assert tree1.in_tree('t1l1.t1l2b1')

	def test_is_leaf(self, default_trees):
		""" Test that the property is_leaf works as expected """
		tree1, tree2, tree3, _ = default_trees
		assert not tree1.is_leaf('t1l1')
		assert not tree2.is_leaf('t2l1.t2l2b1')
		assert tree2.is_leaf('t2l1.t2l2b1.t2l3b1b')
		assert tree3.is_leaf('t3l1')

	def test_make_root_works(self, default_trees):
		""" Test that get_data() method works """
		#   Original tree		Make root tree
		#	root                root.branch1 (*)
		#	├branch1 (*)        ├leaf1
		#	│├leaf1             │└subleaf1 (*)
		#	││└subleaf1 (*)     └leaf2 (*)
		#	│└leaf2 (*)          └subleaf2
		#	│ └subleaf2
		#	└branch2
		_, _, _, tree4 = default_trees
		tree4.make_root('root')
		assert str(tree4) == ('root\n'
							  '├branch1 (*)\n'
							  '│├leaf1\n'
							  '││└subleaf1 (*)\n'
							  '│└leaf2 (*)\n'
							  '│ └subleaf2\n'
							  '└branch2')
		tree4.make_root('root.branch1')
		assert str(tree4) == ('root.branch1 (*)\n'
							  '├leaf1\n'
							  '│└subleaf1 (*)\n'
							  '└leaf2 (*)\n'
							  ' └subleaf2')
		tree4.make_root('root.branch1.leaf2.subleaf2')
		assert str(tree4) == 'root.branch1.leaf2.subleaf2'

	def test_print_node_works(self, default_trees):
		""" Test that the method print_node() works as expected """
		tree1, tree2, tree3, _ = default_trees
		obj = putil.tree.Tree()
		obj.add_nodes([
			{'name':'dtree', 'data':list()},
			{'name':'dtree.my_child', 'data':'Tree 2, level 2'}
		])
		#
		assert tree1.print_node('t1l1') == (
			'Name: t1l1\n'
			'Parent: None\n'
			'Children: t1l2b1, t1l2b2\n'
			'Data: Tree 1, level 1'
		)
		tree2.add_nodes({'name':'t2l1.t2l2b1.t2l3b1b', 'data':14.3})
		assert tree2.print_node('t2l1.t2l2b1.t2l3b1b') == (
			"Name: t2l1.t2l2b1.t2l3b1b\n"
			"Parent: t2l1.t2l2b1\n"
			"Children: None\n"
			"Data: ['Tree 2, level 3, branch 1, child b', 14.3]"
		)
		assert tree3.print_node('t3l1') == (
			'Name: t3l1\n'
			'Parent: None\n'
			'Children: None\n'
			'Data: Tree 3, level 1'
		)
		assert obj.print_node('dtree') == (
			'Name: dtree\n'
			'Parent: None\n'
			'Children: my_child\n'
			'Data: None'
		)

	def test_rename_node_errors(self, default_trees):
		""" Test that the method rename_node() raises the appropriate exceptions """
		_, _, _, tree4 = default_trees
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':5, 'new_name':'root.x'},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'a.b..c', 'new_name':'root.x'},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'a.b.c', 'new_name':'root.x'},
			RuntimeError,
			'Node a.b.c not in tree'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'root', 'new_name':5},
			RuntimeError,
			'Argument `new_name` is not valid'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'root', 'new_name':'a..b'},
			RuntimeError,
			'Argument `new_name` is not valid'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'root.branch1', 'new_name':'root.branch1'},
			RuntimeError,
			'Node root.branch1 already exists'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'root.branch1', 'new_name':'a.b.c'},
			RuntimeError,
			'Argument `new_name` has an illegal root node'
		)
		putil.test.assert_exception(
			tree4.rename_node,
			{'name':'root', 'new_name':'dummy.hier'},
			RuntimeError,
			'Argument `new_name` is an illegal root node name'
		)

	def test_rename_node_works(self, default_trees):
		""" Test that the method rename_node() works as expected """
		_, _, _, tree4 = default_trees
		tree4.rename_node('root.branch1.leaf1', 'root.branch1.mapleleaf1')
		assert str(tree4) == ('root\n'
							  '├branch1 (*)\n'
							  '│├leaf2 (*)\n'
							  '││└subleaf2\n'
							  '│└mapleleaf1\n'
							  '│ └subleaf1 (*)\n'
							  '└branch2')
		tree4.rename_node('root', 'dummy')
		assert str(tree4) == ('dummy\n'
							  '├branch1 (*)\n'
							  '│├leaf2 (*)\n'
							  '││└subleaf2\n'
							  '│└mapleleaf1\n'
							  '│ └subleaf1 (*)\n'
							  '└branch2')
		tobj = putil.tree.Tree()
		tobj.add_nodes([
			{'name':'dummy.levels.root.branch1', 'data':list()},
			{'name':'dummy.levels.root.branch2', 'data':list()},
			{'name':'dummy.levels.root.branch1.leaf1', 'data':list()},
			{'name':'dummy.levels.root.branch1.leaf1.subleaf1', 'data':333},
			{'name':'dummy.levels.root.branch1.leaf2', 'data':'Hello world!'},
			{'name':'dummy.levels.root.branch1.leaf2.subleaf2', 'data':list()},
		])
		tobj.make_root('dummy.levels.root')
		tobj.rename_node('dummy.levels.root', 'top')
		assert str(tobj) == ('top\n'
							 '├branch1\n'
							 '│├leaf1\n'
							 '││└subleaf1 (*)\n'
							 '│└leaf2 (*)\n'
							 '│ └subleaf2\n'
							 '└branch2')

	def test_root_node_works(self, default_trees):
		""" Test that root_node property works """
		tree1, _, _, _ = default_trees
		tree4 = putil.tree.Tree()
		assert tree1.root_node == {
			'parent':'',
			'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
			'data':['Tree 1, level 1']
		}
		assert tree4.root_node is None

	def test_root_name_works(self, default_trees):
		""" Test that root_name property works """
		tree1, _, _, _ = default_trees
		tree4 = putil.tree.Tree()
		assert tree1.root_name == 't1l1'
		assert tree4.root_name is None

	def test_node_separator_property_works(self, default_trees):
		""" Test that node_separator property works """
		tree1, _, _, _ = default_trees
		assert tree1.node_separator == '.'

	def test_cannot_delete_attributes(self, default_trees):
		""" Test that del method raises an exception on all class attributes """
		tree1, _, _, _ = default_trees
		with pytest.raises(AttributeError) as excinfo:
			del tree1.root_node
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del tree1.root_name
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del tree1.node_separator
		assert putil.test.get_exmsg(excinfo) == "can't delete attribute"

	def test_str_works(self, default_trees):
		""" Test that ppstr method works """
		tree1, tree2, tree3, _ = default_trees
		tree1.add_nodes([
			{'name':'t1l1.t1l2b1.t1l3b1a.leaf1', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.leaf3', 'data':list()},
			{'name':'t1l1.t1l2b1.t1l3b1c.leaf2.subleaf4', 'data':list()}
		])
		assert str(tree1) == ('t1l1 (*)\n'
							  '├t1l2b1 (*)\n'
							  '│├t1l3b1a (*)\n'
							  '││└leaf1\n'
							  '│├t1l3b1b (*)\n'
							  '│└t1l3b1c (*)\n'
							  '│ └leaf2\n'
							  '│  ├leaf3\n'
							  '│  └subleaf4\n'
							  '└t1l2b2 (*)\n'
							  ' ├t1l3b2a (*)\n'
							  ' ├t1l3b2b (*)\n'
							  ' └t1l3b2c (*)')
		assert str(tree2) == ('t2l1 (*)\n'
							  '├t2l2b1 (*)\n'
							  '│├t2l3b1a (*)\n'
							  '│├t2l3b1b (*)\n'
							  '│└t2l3b1c (*)\n'
							  '└t2l2b2 (*)\n'
							  ' ├t2l3b2a (*)\n'
							  ' ├t2l3b2b (*)\n'
							  ' └t2l3b2c (*)')
		assert str(tree3) == 't3l1 (*)'
		tree3.add_nodes({'name':'t3l1.leaf1', 'data':list()})
		assert str(tree3) == 't3l1 (*)\n└leaf1'
		tree3.add_nodes({'name':'t3l1.leaf2', 'data':list()})
		assert str(tree3) == 't3l1 (*)\n├leaf1\n└leaf2'

	def test_get_node_parent_works(self, default_trees):
		""" Test that get_node_parent method works """
		tree1, _, _, _ = default_trees
		assert tree1.get_node_parent('t1l1') == dict()
		assert tree1.get_node_parent('t1l1.t1l2b1') == {
			'parent':'',
			'children':['t1l1.t1l2b1', 't1l1.t1l2b2'],
			'data':['Tree 1, level 1']
		}

	def test_private_get_children_works(self, default_trees):
		""" Test _get_children method works """
		tree1, _, _, _ = default_trees
		assert sorted(tree1._get_children('t1l1')) == sorted([
			't1l1.t1l2b1',
			't1l1.t1l2b2'
		])
		assert tree1._get_children('t1l1.t1l2b2.t1l3b2c') == list()

	def test_private_get_parent_works(self, default_trees):
		""" Test _get_parent method works """
		tree1, _, _, _ = default_trees
		assert tree1._get_parent('t1l1') == ''
		assert tree1._get_parent('t1l1.t1l2b2.t1l3b2c') == 't1l1.t1l2b2'

	def test_private_get_data_works(self, default_trees):
		""" Test _get_data method works """
		_, _, _, tree4 = default_trees
		assert tree4._get_data('root.branch1.leaf1') == list()
		assert tree4._get_data('root.branch1') == [5, 7]

	def test_private_set_children_works(self, default_trees):
		""" Test _set_children method works """
		_, _, _, tree4 = default_trees
		tree4._set_children(
			'root.branch1.leaf2',
			[
				'root.branch1.leaf2.c',
				'root.branch1.leaf2.x',
				'root.branch1.leaf2.a'
			]
		)
		assert tree4._get_children('root.branch1.leaf2') == [
			'root.branch1.leaf2.a',
			'root.branch1.leaf2.c',
			'root.branch1.leaf2.x'
		]

	def test_private_set_data_works(self, default_trees):
		""" Test _set_data method works """
		_, _, _, tree4 = default_trees
		tree4._set_data('root.branch1', ['Hello world'])
		assert tree4._get_data('root.branch1') == ['Hello world']

	def test_private_set_parent_works(self, default_trees):
		""" Test _set_parent method works """
		_, _, _, tree4 = default_trees
		tree4._set_parent('root.branch1.leaf2.subleaf2', 'leaf_zzz')
		assert tree4._get_parent('root.branch1.leaf2.subleaf2') == 'leaf_zzz'

	def test_search_tree(self):
		""" Test search() method works """
		tobj = putil.tree.Tree('/')
		tobj.add_nodes([{'name':'root', 'data':list()},
				        {'name':'root/anode', 'data':list()},
				        {'name':'root/bnode', 'data':list()},
				        {'name':'root/cnode', 'data':list()},
		                {'name':'root/bnode/anode', 'data':list()},
		                {'name':'root/cnode/anode/leaf', 'data':list()},
		                {'name':'root/cnode/anode/leaf1', 'data':list()}
		               ])
		putil.test.assert_exception(
			tobj.search_tree,
			{'name':5},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tobj.search_tree,
			{'name':'a/ b'},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tobj.search_tree,
			{'name':'a/b//c'},
			RuntimeError,
			'Argument `name` is not valid'
		)
		assert tobj.search_tree('anode') == sorted([
			'root/anode',
			'root/bnode/anode',
			'root/cnode/anode',
			'root/cnode/anode/leaf',
			'root/cnode/anode/leaf1'
		])
		assert tobj.search_tree('leaf') == sorted(['root/cnode/anode/leaf'])
		tobj = putil.tree.Tree('/')
		tobj.add_nodes([
			{'name':'anode', 'data':list()},
			{'name':'anode/some_node', 'data':list()}
		])
		assert tobj.search_tree('anode') == sorted(['anode', 'anode/some_node'])
		tobj = putil.tree.Tree('/')
		tobj.add_nodes({'name':'anode', 'data':list()})
		assert tobj.search_tree('anode') == sorted(['anode'])

	def test_delete_prefix(self):
		""" Test search() method works """
		tobj = putil.tree.Tree('/')
		tobj.add_nodes([{'name':'hello/world/root', 'data':list()},
				        {'name':'hello/world/root/anode', 'data':7},
				        {'name':'hello/world/root/bnode', 'data':list()},
				        {'name':'hello/world/root/cnode', 'data':list()},
		                {'name':'hello/world/root/bnode/anode', 'data':list()},
		                {'name':'hello/world/root/cnode/anode/leaf', 'data':list()}
		               ])
		putil.test.assert_exception(
			tobj.delete_prefix,
			{'name':5},
			RuntimeError,
			'Argument `name` is not valid'
		)
		putil.test.assert_exception(
			tobj.delete_prefix,
			{'name':'hello/world/root'},
			RuntimeError,
			'Argument `name` is not a valid prefix'
		)
		putil.test.assert_exception(
			tobj.delete_prefix,
			{'name':'hello/world!!!!'},
			RuntimeError,
			'Argument `name` is not a valid prefix'
		)
		tobj.collapse_subtree(tobj.root_name, recursive=False)
		tobj.delete_prefix('hello/world')
		assert str(tobj) == ('root\n'
							 '├anode (*)\n'
							 '├bnode\n'
							 '│└anode\n'
							 '└cnode\n'
							 ' └anode\n'
							 '  └leaf')

	def test_copy_works(self, default_trees):
		""" Test __copy__() method """
		_, _, _, tree4 = default_trees
		ntree = copy.copy(tree4)
		assert id(ntree) != id(tree4)
		assert (ntree._db == tree4._db) and (id(ntree._db) != id(tree4._db))
		assert ntree._root == tree4._root
		assert ntree._root_hierarchy_length is tree4._root_hierarchy_length
		assert ntree._exh is tree4._exh

	def test_find_common_prefix(self):
		""" Test _find_common_prefix() method """
		tobj = putil.tree.Tree('/')
		assert tobj._find_common_prefix(
			'root/hello/world',
			'root/hello'
		) == 'root/hello'
		assert tobj._find_common_prefix('root/hello/world', 'root') == 'root'
		assert tobj._find_common_prefix('root/hello/world', 'branch') == ''

	def test_nonzero(self):
		""" Test __nonzero__() function """
		tobj = putil.tree.Tree()
		assert not tobj
		tobj.add_nodes([{'name':'root.branch1', 'data':5}])
		assert tobj
