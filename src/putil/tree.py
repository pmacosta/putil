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
	def __init__(self, name, left=None, right=None, data=None):	#pylint: disable-msg=R0913
		self._db = dict()
		self.name = name
		self.left = left
		self.right = right
		self.data = data

	def _get_name(self):	#pylint: disable=C0111
		return self._db['name']

	@putil.check.check_argument(putil.check.PolymorphicType([None, str]))
	def _set_name(self, name):	#pylint: disable=C0111
		self._db['name'] = self.name.strip() if name else name

	def _get_left(self):	#pylint: disable=C0111
		return self._db['left']

	@putil.check.check_argument(putil.check.PolymorphicType([None, TreeNode]))
	def _set_left(self, left):	#pylint: disable=C0111
		self._db['left'] = left

	def _get_right(self):	#pylint: disable=C0111
		return self._db['right']

	@putil.check.check_argument(putil.check.PolymorphicType([None, TreeNode, putil.check.ArbitraryLengthList(TreeNode)]))
	def _set_right(self, right):	#pylint: disable=C0111
		# Check that node names are unique
		if self.right and right:
			nodes_to_add = right if isinstance(right, list) else [right]
			for name in [element.name for element in nodes_to_add]:
				if name in self.right_names:
					raise ValueError('Node {0} already to the rigth (down) of current node'.format(name))
		self._db['right'] = ((self.right if self.right else list())+(right if isinstance(right, list) else [right])).sort() if right else right

	def _get_left_name(self):	#pylint: disable=C0111
		return None if not self.left else self.left.name

	def _get_right_names(self):	#pylint: disable=C0111
		return self.right if not self.right else [tright.name for tright in self.right]

	def _get_data(self):	#pylint: disable=C0111
		return self._db['data']

	def _set_data(self, data):	#pylint: disable=C0111
		if self.data and data:
			data = data if isinstance(data, list) else [data]
			for element in data:
				if element in self.data:
					raise ValueError('Node {0} already has {1} as its data'.format(self.name, element))
		self._db['data'] = (self.data if self.data else list())+data if data else data

	def __str__(self):
		return 'Name: {0}\nLeft: {1}\nRight: {2}'.format(self.name, self.left_name, self.right_names)

	def prt(self, tab=0):
		"""
		Pretty print tree as a character-based tree structure
		"""
		subtree = 'False' if not self.right else (False if not len(self.right) else True)
		if subtree is True:
			for tree in self.right:
				tree.prt(tab+1)

	# Managed attributes
	name = property(_get_name, _set_name, None, doc='Name of tree node')
	"""
	:param	name: Name of tree node
	:type	name: string
	:rtype	name: string
	:raises: TypeError (Argument `name` is of the wrong type)
	"""	#pylint: disable=W0105

	left = property(_get_left, _set_left, None, doc='Left (up) node object with respect to current node')
	"""
	:param	left: Node to the left (up) of current node
	:type	left: :py:class:`putil.tree.TreeNode()` object
	:rtype	left: :py:class:`putil.tree.TreeNode()` object
	:raises: TypeError (Argument `left` is of the wrong type)
	"""	#pylint: disable=W0105

	right = property(_get_right, _set_right, None, doc='Right (down) node object(s) with respect to current node')
	"""
	:param	right: Node(s) to the right (down) of current node
	:type	right: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
	:rtype	right: :py:class:`putil.tree.TreeNode()` object or list of :py:class:`putil.tree.TreeNode()` objects
	:raises:
	 * TypeError (Argument `right` is of the wrong type)

	 * ValueError (Node *[node_name]* already to the rigth (down) of current node)
	"""	#pylint: disable=W0105

	left_name = property(_get_left_name, None, None, doc='Node name to the left (up) of current node')
	"""
	Node name to the left (up) of current node, None if node is root
	:rtype	name: string, or None
	"""	#pylint: disable=W0105

	right_names = property(_get_right_names, None, None, doc='Node name to the right (down) of current node')
	"""
	Node names to the right (down) of current node, None if node is a leaf
	:rtype	name: string, list of strings or None
	"""	#pylint: disable=W0105

	data = property(_get_data, _set_data, None, doc='Data of tree node')
	"""
	:param	data: Data of tree node
	:type	data: any type or list of any type
	:rtype	data: any type or list of any type
	:raises: TypeError ('Node *[node_name]* already has *[element]* as its data')
	"""	#pylint: disable=W0105


@putil.check.check_arguments({'tree':TreeNode, 'name':str})
def search_for_node(tree, name):
	"""
	Searches tree object for a particular node name. Returns *None* if node name not found.

	:param	tree:	Tree to search
	:type	tree:	:py:class:`putil.tree.TreeNode()` object
	:param	name:	Node name to search for (case sensitive)
	:type	name:	string
	:rtype:	:py:class:`putil.tree.TreeNode()` object or None
	"""
	if tree.name == name:
		return tree
	if not tree.right:
		return None
	for subtree in tree.right:
		if search_for_node(subtree, name):
			return subtree
	return None

@putil.check.check_arguments({'tree':TreeNode, 'name':str})
def search_for_node_hierarchical(tree, name):
	"""
	Searches tree object for a particular node hierarchy.  Returns *None* if node name not found.

	:param	tree:	Tree to search
	:type	tree:	:py:class:`putil.tree.TreeNode()` object
	:param	name:	Node name to search for (case sensitive). Levels of hierarchy are denoted by '.', for example 'root.branch1.leaf2'.
	:type	name:	string
	:rtype:	:py:class:`putil.tree.TreeNode()` object or None
	"""
	if tree.name == name:
		return tree
	if not tree.right:
		return None
	hier = name.split('.')
	print hier
	for subtree in tree.right:
		if search_for_node(subtree, name):
			return subtree
	return None
