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

	:param	name: Name of root node
	:type	name: string
	:param	data: Node data, default is *None*
	:type	data: any type or list of any type
	:raises:
	 * Same as :py:attr:`putil.tree.Tree.name`

	 * Same as :py:attr:`putil.tree.TreeNode.data`
	"""
	@putil.check.check_arguments({'name':NodeName(), 'data':putil.check.Any()})
	def __init__(self, name, data=None):	#pylint: disable-msg=R0913
		self._db = {'name':name, 'payload':{'parent':None, 'children':None, 'data':data}}

	def _node_in_tree(self, name):	#pylint: disable=C0111
		""" Validates that node name is in tree structure """
		if name not in self._db:
			raise RuntimeError('Node {0} not in tree'.format(name))

	@putil.check.check_argument(NodeName())
	def in_tree(self, name):
		"""
		Search tree for a paticular node

		:param	name: Node name to search for
		:type	name: string
		:rtype	data: boolean
		:raises:
		 * TypeError (Argument `name` is of the wrong type)
		"""
		return name in self._db

	@putil.check.check_argument(NodeName())
	def get_parent(self, name):	#pylint: disable=C0111
		"""
		Retrieves parent of a node

		:param	name: Child node name
		:type	name: string
		:rtype	data: string
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]['parent']

	@putil.check.check_arguments({'name':NodeName(), 'parent':NodeName()})
	def set_parent(self, name, parent):	#pylint: disable=C0111
		"""
		Sets parent of a node

		:param	name: Child node name
		:type	name: string
		:param	name: Parent node name
		:type	name: string
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * TypeError (Argument `parent` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)

		 * RuntimeError (Node *[parent]* not in tree)
		"""
		self._node_in_tree(name)
		self._node_in_tree(parent)
		# Remove child from former parent
		children = self.get_children(self.get_parent(name))
		self.set_children(self.get_parent(name), None if (not isinstance(children, list)) or (isinstance(children, list) and (len(children) == 1)) else [node for node in children if node != name])
		# Add child to new parent
		self._db[name]['parent'] = parent
		self.add_children(parent, name)

	@putil.check.check_arguments({'parent':NodeName(), 'children':putil.check.PolymorphicType([NodeName(), putil.check.ArbitraryLengthList(NodeName())])})
	def add_children(self, parent, children):
		"""
		Add children to current node

		:param	name: Child node name
		:type	name: string
		:param	children: Children node(s) to add
		:type	children: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
		:raises:
		 * TypeError (Argument `parent` is of the wrong type)

		 * TypeError (Argument `children` is of the wrong type)

		 * ValueError (Argument `children` has repeated children)

		 * ValueError (Node *[node_name]* is already a child of current node)

		 * RuntimeError (Node *[parent]* not in tree)
		"""
		self._node_in_tree(parent)
		children = children if not children else (children if isinstance(children, list) else [children])
		if children and (len(set(children)) != len(children)):
			raise ValueError('Argument `children` has repeated children')
		# Check that node names are unique
		if self.get_children(parent) and children:
			for name in [child.name for child in children]:
				if name in self.get_children(parent):
					raise ValueError('Node {0} is already a child of parent node {1}'.format(name, parent))
		self.set_children(parent, (self.get_children(parent) if self.get_children(parent) else list())+children if children else self.get_children(parent))

	def get_children(self, name):	#pylint: disable=C0111
		"""
		Retrieves children of a node

		:param	name: Node name
		:type	name: string
		:rtype	data: string
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]['children']

	@putil.check.check_arguments({'parent':NodeName(), 'children':putil.check.PolymorphicType([NodeName(), putil.check.ArbitraryLengthList(NodeName())]), 'data':putil.check.PolymorphicType([None, putil.check.Any()])})
	def set_children(self, parent, children, data=None):	#pylint: disable=C0111
		"""
		Sets children of a node

		:param	name: Parent node name
		:type	name: string
		:param	name: Child node name(s)
		:type	name: string or list of strings
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * TypeError (Argument `parent` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)

		 * RuntimeError (Node *[parent]* not in tree)
		"""
		self._node_in_tree(parent)
		children = children if not children else (children if isinstance(children, list) else [children])
		if children and (len(set(children)) != len(children)):
			raise ValueError('Argument `children` has repeated children')
		for child in children:
			names = child.split('.')
			if len(names) == 1:
				raise ValueError('Invalid child name: {0}'.format(child))
			if '.'.join(names[:-1]) != parent:
				raise ValueError('Invalid child root name')
		self._db[parent]['children'] = children
		if self.get_children(parent):
			for child in self.get_children(parent):
				self._db[child] = {'parent':parent, 'children':None, 'data':data}

	@putil.check.check_argument(NodeName())
	def get_node(self, name):	#pylint: disable=C0111
		"""
		Get tree node in the form of a dictionary with three keys, *parent* (parent node name), *children* (node name or list of node names containing child(ren) node name(s)) and *data* (node data).

		:param	name: Node name
		:type	name: string
		:rtype: dictionary
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]

	@putil.check.check_argument(NodeName())
	def get_data(self, name):	#pylint: disable=C0111
		"""
		Get node data

		:param	name: Node name
		:type	name: string
		:type	data: any type or list of any type
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return self._db[name]['data']

	@putil.check.check_arguments({'name':NodeName(), 'data':putil.check.Any()})
	def set_data(self, name, data):	#pylint: disable=C0111
		"""
		Set node data

		:param	name: Node name
		:type	name: string
		:param	data: Node data
		:type	data: any type or list of any type
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		self._db[name]['data'] = data

	@putil.check.check_arguments({'name':NodeName(), 'data':putil.check.Any()})
	def add_data(self, name, data):	#pylint: disable=C0111
		"""
		Add data to node

		:param	name: Node name
		:type	name: string
		:param	data: Node data
		:type	data: any type or list of any type
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		self._db[name]['data'] = (data if not self.get_data(name) else (self.get_data(name) if isinstance(self.get_data(name), list) else [self.get_data(name)])+[data]) if (data is not None) else self.get_data(name)

	def __str__(self):
		u"""
		String with the tree structure pretty printed as a character-based tree structure. Only node names are shown, nodes with data are marked with an asterisk (*). For example:

			>>> import putil.tree
			>>> tleaf1 = putil.tree.TreeNode(name='leaf1')
			>>> tleaf2 = putil.tree.TreeNode(name='leaf2', data='Hello world!')
			>>> tbranch1 = putil.tree.TreeNode(name='branch1', children=[tleaf1, tleaf2], data=5)
			>>> tbranch2 = putil.tree.TreeNode(name='branch2')
			>>> tobj=putil.tree.TreeNode(name='root', children=[tbranch1, tbranch2])
			>>> tobj.ppstr
			root
			├branch1 (*)
			│├leaf1
			│└leaf2 (*)
			└branch2

		:rtype: Unicode string
		"""
		return self._prt(name=None)

	def _prt(self, name, sep=unichr(0x2502), last=False):	#pylint: disable=C0111
		# Characters from http://www.unicode.org/charts/PDF/U2500.pdf
		name = name if name is not None else sorted(self._db.keys())[0]
		ret = [(sep+(unichr(0x251C) if not last else unichr(0x2514)) if not self.is_root(name) else '')+name+(' (*)' if self.get_data(name) else '')]
		ret += [self._prt(child, sep='' if self.is_root(child) else (sep+(unichr(0x2502) if not last else ' ')), last=child == self.get_children(name)[-1]) for child in self.get_children(name)] if not self.is_leaf(name) else list()
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

		 * RuntimeError (Node *[name]* not in tree)
		"""
		self._node_in_tree(name)
		return True if not self.get_parent(name) else False

	@putil.check.check_argument(NodeName())
	def is_leaf(self, name):	#pylint: disable=C0111
		"""
		Leaf node flag, *True* if node is a leaf node (node with no children), *False* otherwise

		:param	name: Node name
		:type	name: string
		:rtype: boolean
		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * RuntimeError (Node *[name]* not in tree)
		"""
		return True if not self.get_children(name) else False


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
def build_tree(tree_info):
	"""
	Builds tree object

	:param	tree_info:	Tree information. Each dictionary must contain only two keys, *node*, with a (hierarchical) node name, and *data*, with the node data. Multiple entries for a given node name may exist, \
	and the resulting node data will be a list whose elements are the values of the *data* key of all dictionaries in **tree_info** that share the same node name
	:type	tree_info:	dictionary or list of dictionaries.
	:rtype:	:py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects if there are multiple root nodes
	:raises:
	 * TypeError (Argument `tree_info` is of the wrong type)

	 * Same as :py:attr:`putil.tree.TreeNode.name`
	"""
	roots = list()
	tree_dict_list = tree_info if isinstance(tree_info, list) else [tree_info]
	for node_dict in tree_dict_list:
		name = node_dict['node']
		data = node_dict['data']
		names = [element.strip() for element in name.strip().split('.')]
		# Find or create tree to add nodes and data to
		for root in roots:
			tobj = search_for_node(root, names[0])
			if tobj:
				break
		else:
			tobj = Tree(name=names[0])
			roots.append(tobj)
		# Search for leaf node and create children as appropriate
		for num, node_name in enumerate(names):
			if not search_for_node(tobj, '.'.join(names[:num+1])):
				tobj.add_children('.'.join(names[:num]), node_name)
		# Add data
		tobj.add_data(name, data)
	return roots[0] if len(roots) == 1 else (None if not roots else roots)
