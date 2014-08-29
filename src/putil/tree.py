# pylint: disable=W0212
# tree.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Lightweight tree structure
"""


import putil.check


class TreeNode(object):	#pylint: disable=R0903
	"""
	Basic tree hierarchy/linked list
	"""
	def __init__(self, name, parent=None, children=None, data=None):	#pylint: disable-msg=R0913
		self._db = {'name':None, 'parent':None, 'children':None, 'data':None}
		self.name = name
		self.parent = parent
		self.children = children
		self.data = data

	def _get_name(self):	#pylint: disable=C0111
		return self._db['name']

	@putil.check.check_argument(putil.check.PolymorphicType([None, str]))
	def _set_name(self, name):	#pylint: disable=C0111
		self._db['name'] = name.strip() if name else name

	def _get_parent(self):	#pylint: disable=C0111
		return self._db['parent']

	def _set_parent(self, parent):	#pylint: disable=C0111
		if (parent is not None) and (not isinstance(parent, TreeNode)):
			raise TypeError('Argument `parent` is of the wrong type')
		self._db['parent'] = parent
		if self.parent:
			self.parent.add_children(self)

	def add_children(self, children):
		"""
		Add children to current node
		:param	children: Children node(s) to add
		:type	children: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
		:raises:
		 * TypeError (Argument `children` is of the wrong type)

		 * ValueError (Argument `children` has repeated children)

		 * ValueError (Node *[node_name]* is already a child of current node)
		"""
		if (children is not None) and ((not isinstance(children, list) and (not isinstance(children, TreeNode))) or (isinstance(children, list) and any([not isinstance(child, TreeNode) for child in children]))):
			raise TypeError('Argument `children` is of the wrong type')
		children = children if not children else (children if isinstance(children, list) else [children])
		if children and (len(set(children)) != len(children)):
			raise ValueError('Argument `children` has repeated children')
		# Check that node names are unique
		if self.children and children:
			for name in [child.name for child in children]:
				if name in self.children_names:
					raise ValueError('Node {0} is already a child of current node'.format(name))
		self.children = (self.children if self.children else list())+children if children else self.children

	def collapse(self):
		""" Elliminates nodes that only have only one child and no data """
		while True:
			if (not self.is_leaf) and (not self.data) and (len(self.children) == 1):
				self.name = self.name+'.'+self.children[0].name
				self.data = self.children[0].data
				self.children = self.children[0].children
			else:
				break
		if not self.is_leaf:
			for child in self.children:
				child.collapse()

	def _get_children(self):	#pylint: disable=C0111
		return self._db['children']

	def _set_children(self, children):	#pylint: disable=C0111
		if (children is not None) and ((not isinstance(children, list) and (not isinstance(children, TreeNode))) or (isinstance(children, list) and any([not isinstance(child, TreeNode) for child in children]))):
			raise TypeError('Argument `children` is of the wrong type')
		children = children if not children else (children if isinstance(children, list) else [children])
		if children and (len(set(children)) != len(children)):
			raise ValueError('Argument `children` has repeated children')
		self._db['children'] = children
		if self.children:
			for child in self.children:
				child._db['parent'] = self

	def _get_parent_name(self):	#pylint: disable=C0111
		return None if not self.parent else self.parent.name

	def _get_children_names(self):	#pylint: disable=C0111
		return self.children if not self.children else [node.name for node in self.children]

	def _get_data(self):	#pylint: disable=C0111
		return self._db['data']

	def _set_data(self, data):	#pylint: disable=C0111
		self._db['data'] = data

	def add_data(self, data):	#pylint: disable=C0111
		self.data = (data if not self.data else (self.data if isinstance(self.data, list) else [self.data])+[data]) if (data is not None) else self.data

	def __str__(self):
		children_names_txt = None if not self.children_names else (self.children_names[0] if len(self.children_names) == 1 else ', '.join(self.children_names))
		return 'Name: {0}\nParent: {1}\nChildren: {2}\nData: {3}'.format(self.name, self.parent_name, children_names_txt, self.data)

	def pprint(self):
		""" Pretty print tree as a character-based tree structure """
		return self._prt()

	def _prt(self, sep=unichr(0x2502), last=False):	#pylint: disable=C0111
		# Characters from http://www.unicode.org/charts/PDF/U2500.pdf
		ret = [(sep+(unichr(0x251C) if not last else unichr(0x2514)) if not self.is_root else '')+self.name]
		ret += [tree._prt(sep='' if self.is_root else (sep+(unichr(0x2502) if not last else ' ')), last=tree == self.children[-1]) for tree in self.children] if not self.is_leaf else list()
		return '\n'.join(ret)

	def _get_is_root(self):	#pylint: disable=C0111
		return True if not self.parent else False

	def _get_is_leaf(self):	#pylint: disable=C0111
		return True if not self.children else False

	# Managed attributes
	children = property(_get_children, _set_children, None, doc='Children node object(s) of current node')
	"""
	:param	children: Children node(s) of current node
	:type	children: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
	:rtype: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
	:raises:
	 * TypeError (Argument `children` is of the wrong type)

	 * ValueError (Argument `children` has repeated children)
	"""	#pylint: disable=W0105

	children_names = property(_get_children_names, None, None, doc='Node name to the children (down) of current node')
	"""
	Node names to the children (down) of current node, None if node is a leaf
	:rtype: string, list of strings or None
	"""	#pylint: disable=W0105

	is_leaf = property(_get_is_leaf, None, None, doc='Leaf node flag')
	"""
	Leaf node flag, *True* if current node is a leaf node (node with no children), *False* otherwise
	:rtype: boolean
	"""	#pylint: disable=W0105

	is_root = property(_get_is_root, None, None, doc='Root node flag')
	"""
	Root node flag, *True* if current node is the root node (node with no ancestors), *False* otherwise
	:rtype: boolean
	"""	#pylint: disable=W0105

	data = property(_get_data, _set_data, None, doc='Data of tree node')
	"""
	:param	data: Data of tree node
	:type	data: any type or list of any type
	:rtype: any type or list of any type
	:raises: TypeError ('Node *[node_name]* already has *[element]* as its data')
	"""	#pylint: disable=W0105

	name = property(_get_name, _set_name, None, doc='Name of tree node')
	"""
	:param	name: Name of tree node
	:type	name: string
	:rtype: string
	:raises: TypeError (Argument `name` is of the wrong type)
	"""	#pylint: disable=W0105

	parent = property(_get_parent, _set_parent, None, doc='Parent node object of current node')
	"""
	:param	parent: Parent of current node
	:type	parent: :py:class:`putil.tree.TreeNode()` object
	:rtype: :py:class:`putil.tree.TreeNode()` object
	:raises: TypeError (Argument `parent` is of the wrong type)
	"""	#pylint: disable=W0105

	parent_name = property(_get_parent_name, None, None, doc='Parent node name of current node')
	"""
	Parent node name of current node, *None* if node is root
	:rtype: string, or None
	"""	#pylint: disable=W0105


@putil.check.check_arguments({'tree':TreeNode, 'name':str})
def search_for_node(tree, name):
	"""
	Searches tree node and its children for a particular node name, which can be specified hierarchically. Returns *None* if node name not found.

	:param	tree:	Root node of the tree to search
	:type	tree:	:py:class:`putil.tree.TreeNode()` object
	:param	name:	Node name to search for (case sensitive). Levels of hierarchy are denoted by '.', for example 'root.branch1.leaf2'.
	:type	name:	string
	:rtype:	:py:class:`putil.tree.TreeNode()` object or *None* if node not found
	:raises: ValueError (Node name is empty)
	"""
	if not name.strip():
		raise ValueError('Node name is empty')
	names = [element.strip() for element in name.strip().split('.')]
	name_options = ['.'.join(names[:num]) for num in range(len(names), 0, -1)]
	names_left = ['.'.join(names[num:len(names)]) for num in range(len(names), 0, -1)]
	node_name, leftover_node_names = None, None
	for node_name, leftover_node_names in zip(name_options, names_left):
		if (tree.name == node_name) and (node_name == name_options[0]):
			return tree
		elif tree.name == node_name:
			break
	else:
		return None
	if tree.children:
		for child in tree.children:
			result = search_for_node(child, leftover_node_names)
			if result:
				return result
	return None
