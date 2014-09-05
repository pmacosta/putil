# -*- coding: utf-8 -*-
# pylint: disable=W0212,C0111
# tree.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details


import putil.check

###
# Node name custom pseudo-type
###
class NodeName(object):	#pylint: disable=R0903
	""" Hierarchical node name data type class """
	def includes(self, test_obj):	#pylint: disable=R0201,W0613
		"""	Test that an object belongs to the pseudo-type """
		return False if (not isinstance(test_obj, str)) or (isinstance(test_obj, str) and (' ' in test_obj)) else all([element.strip() != '' for element in test_obj.strip().split('.')])

	def istype(self, test_obj):	#pylint: disable=R0201
		"""	Checks to see if object is of the same class type """
		return isinstance(test_obj, str)

	def exception(self, param_name):	#pylint: disable=R0201,W0613
		"""	Returns a suitable exception message """
		exp_dict = dict()
		exp_dict['type'] = ValueError
		exp_dict['msg'] = 'Argument `{0}` is not a valid node name'.format(param_name)
		return exp_dict
putil.check.register_new_type(NodeName, 'Hierarchical node name')


class Tree(object):	#pylint: disable=R0903
	"""
	Provides basic data tree functionality

	:rtype: :py:class:`putil.tree.Tree()` object
	"""
	def __init__(self):	#pylint: disable=R0913
		self._db = dict()
		self._root = None
		#{'name':{'parent':None, 'children':None, 'data':data}}

	def _get_root_node(self):	#pylint: disable=C0111
		return None if not self.root_name else self.get_node(self.root_name)

	def _get_root_name(self):	#pylint: disable=C0111
		return self._root

	def _node_in_tree(self, name):	#pylint: disable=C0111
		if name not in self._db:
			raise RuntimeError('Node {0} not in tree'.format(name))

	def _set_root_name(self, name):	#pylint: disable=C0111
		self._root = name

	def _split_node_name(self, name):	#pylint: disable=C0111,R0201
		return [element.strip() for element in name.strip().split('.')]

	@putil.check.check_argument(putil.check.PolymorphicType([{'name':NodeName(), 'data':putil.check.Any()}, putil.check.ArbitraryLengthList({'name':NodeName(), 'data':putil.check.Any()})]))
	def add(self, nodes):
		"""
		Add nodes to tree

		:param	nodes: Node(s) to add. Each dictionary must contain these exactly two entries, **name** (*string*) node name, and **data** (*any* or None) node data. If there are several list elements that refer to the same \
		node the resulting node data is a list with all the data of the elements that have the same node name in addition to any existing data if the node is already present in the tree list element(s) that refer to an existing node.
		:type	nodes: dictionary or list of dictionaries
		:raises:
		 * TypeError (Argument `nodes` is of the wrong type)

		 * ValueError (Illegal node name *[node_name]*)
		"""
		nodes = nodes if isinstance(nodes, list) else [nodes]
		if not self.root_name:
			self._set_root_name(nodes[0]['name'].split('.')[0].strip())
			self._db[self.root_name] = {'parent':'', 'children':list(), 'data':list()}
		for node_dict in nodes:
			name = node_dict['name']
			data = node_dict['data']
			if not self.in_tree(name):
				hierarchy = self._split_node_name(name)
				if hierarchy[0] != self.root_name:
					raise ValueError('Illegal node name: {0}'.format(name))
				for num in range(len(hierarchy)):
					child = '.'.join(hierarchy[:num+1])
					if not self.in_tree(child):
						parent = '.'.join(self._split_node_name(child)[:-1])
						self._db[child] = {'parent':parent, 'children':list(), 'data':list()}
						self._db[parent]['children'] = list(sorted(set(self._db[parent]['children']+[child])))
			data = data if isinstance(data, list) and (len(data) > 0) else (list() if isinstance(data, list) else [data])
			self._db[name]['data'] = self._db[name]['data']+data

	@putil.check.check_argument(putil.check.PolymorphicType([NodeName(), putil.check.ArbitraryLengthList(NodeName())]))
	def delete(self, nodes):
		"""
		Delete nodes (and their sub-trees) from tree

		:param	nodes: Node(s) to delete
		:type	nodes: string or list of strings
		:raises:
		 * TypeError (Argument `nodes` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[node_name]* not in tree)
		"""
		nodes = nodes if isinstance(nodes, list) else [nodes]
		for node in nodes:
			self._node_in_tree(node)
			parent = '.'.join(self._split_node_name(node)[:-1])
			# Delete link to parent (if not root node)
			if parent:
				self._db[parent]['children'] = [child for child in self._db[parent]['children'] if child != node]
			# Delete children (sub-tree)
			for child in [key for key in self._db.keys() if key[:len(node)] == node]:
				del self._db[child]
			if not len(self._db):
				self._root = None

	@putil.check.check_argument(NodeName())
	def get_node(self, name):	#pylint: disable=C0111
		"""
		Get tree node in the form of a dictionary with three keys:
		 * *parent* (*string*) Parent node name, *''* if not is root

		 * *children* (*list*) Node names, empty list if node is a leaf

		 * *data* (*list*) Node data, empty list if node contains no data

		:param	name: Node name
		:type	name: string
		:rtype: dictionary
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]

	@putil.check.check_argument(NodeName())
	def get_node_parent(self, name):	#pylint: disable=C0111
		"""
		Retrieves parent structure of a node. See :py:meth:`putil.tree.Tree.get_node()` for details about returned dictionary.

		:param	name: Child node name
		:type	name: string
		:rtype: dictionary
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[self._db[name]['parent']] if not self.is_root(name) else {}

	@putil.check.check_argument(NodeName())
	def get_children(self, name):	#pylint: disable=C0111
		"""
		Retrieves children of a node

		:param	name: Node name
		:type	name: string
		:rtype	data: listg of strings
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return sorted(self._db[name]['children'])

	@putil.check.check_argument(NodeName())
	def get_data(self, name):	#pylint: disable=C0111
		"""
		Get node data

		:param	name: Node name
		:type	name: string
		:type	data: any type or list of any type
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]['data']

	@putil.check.check_argument(NodeName())
	def in_tree(self, name):
		"""
		Search tree for a paticular node

		:param	name: Node name to search for
		:type	name: string
		:rtype	data: boolean
		:raises: TypeError (Argument `name` is of the wrong type)
		"""
		return name in self._db

	@putil.check.check_argument(NodeName())
	def print_node(self, name):	#pylint: disable=C0111
		"""
		Prints node information

		:param	name: Node name
		:type	name: string
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		node = self.get_node(name)
		children = [self._split_node_name(child)[-1] for child in node['children']] if node['children'] else node['children']
		data = node['data'][0] if node['data'] and (len(node['data']) == 1) else node['data']
		return 'Name: {0}\nParent: {1}\nChildren: {2}\nData: {3}'.format(name, node['parent'] if node['parent'] else None, ', '.join(children) if children else None, data if data else None)

	def __str__(self):
		u"""
		String with the tree structure pretty printed as a character-based tree structure. Only node names are shown, nodes with data are marked with an asterisk (*). For example:

			>>> import putil.tree
			>>> tobj = putil.tree.Tree()
			>>> tobj.add([
			...		{'name':'root.branch1', 'data':5},
			...		{'name':'root.branch2', 'data':None},
			...		{'name':'root.branch1.leaf1', 'data':None},
			...		{'name':'root.branch1.leaf2', 'data':'Hello world!'}
			... ])
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			│└leaf2 (*)
			└branch2

		:rtype: Unicode string
		"""
		return self._prt(name=None).encode('utf-8')

	def _prt(self, name, sep='', last=False):	#pylint: disable=C0111
		# Characters from http://www.unicode.org/charts/PDF/U2500.pdf
		vertical = unichr(0x2502)
		vertical_and_right = unichr(0x251C)
		up_and_right = unichr(0x2514)
		name = name if name is not None else sorted(self._db.keys())[0]
		node_name = name.split('.')[-1]
		ret = [(sep+(vertical_and_right if not last else up_and_right) if not self.is_root(name) else '')+node_name+(' (*)' if self.get_data(name) else '')]
		ret += [self._prt(child, sep='' if self.is_root(name) else (sep+(vertical if not last else ' ')), last=child == self.get_children(name)[-1]) for child in self.get_children(name)] if not self.is_leaf(name) else list()
		return '\n'.join(ret)

	@putil.check.check_argument(NodeName())
	def is_root(self, name):	#pylint: disable=C0111
		"""
		Root node flag, *True* if node is the root node (node with no ancestors), *False* otherwise

		:param	name: Node name
		:type	name: string
		:rtype: boolean
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return not self._db[name]['parent']

	@putil.check.check_argument(NodeName())
	def is_leaf(self, name):	#pylint: disable=C0111
		"""
		Leaf node flag, *True* if node is a leaf node (node with no children), *False* otherwise

		:param	name: Node name
		:type	name: string
		:rtype: boolean
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `nodes` is not a valid node name)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return not self._db[name]['children']

	# Managed attributes
	root_node = property(_get_root_node, None, None, doc='Tree root node')
	"""
	Tree root node or *None* if :py:class:`putil.tree.Tree()` object has no nodes. See :py:meth:`putil.tree.Tree.get_node()` for details about returned dictionary.

	:rtype: dictionary or None
	"""	#pylint: disable=W0105

	root_name = property(_get_root_name, None, None, doc='Tree root node name')
	"""
	Tree root node name, *None* if :py:class:`putil.tree.Tree()` object has no nodes.

	:rtype: string or None
	"""	#pylint: disable=W0105

@putil.check.check_arguments({'tree':Tree, 'name':NodeName()})
def search_for_node(tree, name):
	"""
	Searches tree node and its children for a particular node name, which can be specified hierarchically. Returns *None* if node name not found.

	:param	tree:	Tree to search
	:type	tree:	:py:class:`putil.tree.Tree()` object
	:param	name:	Node name to search for (case sensitive). Levels of hierarchy are denoted by '.', for example 'root.branch1.leaf2'.
	:type	name:	string
	:rtype:	same as :py:meth:`putil.tree.Tree.get_node()` or *None*
	:raises:
	 * TypeError (Argument `tree` is of the wrong type)

	 * TypeError (Argument `name` is of the wrong type)
	"""
	return None if not tree.in_tree(name) else tree.get_node(name)

@putil.check.check_argument(putil.check.PolymorphicType([{'node':NodeName(), 'data':putil.check.Any()}, putil.check.ArbitraryLengthList({'node':NodeName(), 'data':putil.check.Any()})]))
def build_trees(nodes):
	"""
	Build tree objects

	:param	nodes:	Tree information. Each dictionary must contain only two keys, *name*, with a (hierarchical) node name, and *data*, with the node data. Multiple entries for a given node name may exist, \
	and the resulting node data will be a list whose elements are the values of the *data* key of all dictionaries in **tree_info** that share the same node name
	:type	nodes:	dictionary or list of dictionaries.
	:rtype:	:py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects if there are multiple root nodes
	:raises:
	 * TypeError (Argument `tree_info` is of the wrong type)

	 * Same as :py:attr:`putil.tree.TreeNode.name`
	"""
	roots = list()
	nodes = nodes if isinstance(nodes, list) else [nodes]
	for node in nodes:
		root_name = [element.strip() for element in node['name'].strip().split('.')][0]
		# Find or create tree to add nodes and data to
		for tobj in roots:
			if tobj.root_name == root_name:
				break
		else:
			tobj = Tree()
			roots.append(tobj)
		tobj.add(node)
	return roots
