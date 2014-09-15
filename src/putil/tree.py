# -*- coding: utf-8 -*-
# pylint: disable=W0212,C0111
# tree.py
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details


import copy
import inspect

import putil.exh
import putil.check


# Exception tracing initialization code
"""
[[[cog
import sys
import copy
import tempfile

import putil.exh
import putil.misc
import putil.pcsv

mod_obj = sys.modules['__main__']

# Trace Tree class
setattr(mod_obj, '_EXH', putil.exh.ExHandle(putil.tree.Tree))
exobj = getattr(mod_obj, '_EXH')
obj = putil.tree.Tree()
obj.add([
	{'name':'root.branch1', 'data':list()},
	{'name':'root.branch2', 'data':list()},
	{'name':'root.branch1.leaf1', 'data':list()},
	{'name':'root.branch1.leaf1.subleaf1', 'data':333},
	{'name':'root.branch1.leaf2', 'data':'Hello world!'},
	{'name':'root.branch1.leaf2.subleaf2', 'data':list()},
])
obj.collapse('root.branch1')
obj.copy_subtree('root.branch1', 'root.branch3')
obj.delete('root.branch2')
obj.flatten_subtree('root.branch1')
obj.get_node('root')
obj.get_node_children('root')
obj.get_node_parent('root.branch1.leaf1.subleaf1')
obj.get_children('root')
obj.get_leafs('root')
obj.get_data('root')
obj.in_tree('root')
obj.is_root('root')
obj.is_leaf('root')
obj.make_root('root.branch1.leaf2')
exobj.build_ex_tree(no_print=True)
exobj_tree = copy.deepcopy(exobj)
]]]
[[[end]]]
"""	#pylint: disable=W0105


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
		return {'type':ValueError, 'msg':'Argument `{0}` is not a valid node name'.format(param_name)}
putil.check.register_new_type(NodeName, 'Hierarchical node name')


class Tree(object):	#pylint: disable=R0903
	"""
	Provides basic trie (radix tree) functionality

	:rtype: :py:class:`putil.tree.Tree()` object
	"""
	def __init__(self):	#pylint: disable=R0913
		self._db = dict()
		self._root = None
		self._root_hierarchy_length = None
		self._vertical = unichr(0x2502)
		self._vertical_and_right = unichr(0x251C)
		self._up_and_right = unichr(0x2514)
		root_module = inspect.stack()[-1][0]
		self._exh = root_module.f_locals['_EXH'] if '_EXH' in root_module.f_locals else putil.exh.ExHandle(putil.tree.Tree)

	def __str__(self):
		u"""
		String with the tree structure 'pretty printed' as a character-based tree structure. Only node names are shown, nodes with data are marked with an asterisk (*). For example:

			>>> import putil.tree
			>>> tobj = putil.tree.Tree()
			>>> tobj.add([
			...		{'name':'root.branch1', 'data':5},
			...		{'name':'root.branch2', 'data':list()},
			...		{'name':'root.branch1.leaf1', 'data':list()},
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
		return self._prt(name=self.root_name, lparent=-1, sep='', pre1='', pre2='').encode('utf-8')

	def _collapse_node(self, name):
		""" Collapse a sub-tree """
		# This method accesses the database object directly and not through methods (as ideally) because of speed
		node = self._db[name]
		while (len(node['children']) == 1) and (not node['data']):
			child_name = node['children'][0]
			self._db[child_name]['parent'] = node['parent']
			self._db[self._db[name]['parent']]['children'].remove(name)
			self._db[self._db[name]['parent']]['children'] = sorted(self._db[self._db[name]['parent']]['children']+[child_name])
			del self._db[name]
			name = child_name
			node = self._db[name]
		for name in copy.deepcopy(node['children']):
			self._collapse_node(name)

	def _get_nodes(self):	#pylint: disable=C0111
		return None if not self._db else sorted(self._db.keys())

	def _get_root_node(self):	#pylint: disable=C0111
		return None if not self.root_name else self.get_node(self.root_name)

	def _get_root_name(self):	#pylint: disable=C0111
		return self._root

	def _node_in_tree(self, name):	#pylint: disable=C0111
		self._exh.ex_add(name='node_not_in_tree', extype=RuntimeError, exmsg='Node *[node_name]* not in tree')
		self._exh.raise_exception_if(name='node_not_in_tree', condition=name not in self._db, edata={'field':'node_name', 'value':name})
		return True

	def _prt(self, name, lparent, sep, pre1, pre2):	#pylint: disable=C0111,R0913,R0914
		# Characters from http://www.unicode.org/charts/PDF/U2500.pdf
		node_name = name[lparent+1:]
		#node_name = name.split('.')[-1]
		children = self._db[name]['children']
		ncmu = len(children)-1
		plist1 = ncmu*[self._vertical_and_right]+[self._up_and_right]
		plist2 = ncmu*[self._vertical]+[' ']
		slist = (ncmu+1)*[sep+pre2]
		dmark = ' (*)' if self._db[name]['data'] else ''
		return '\n'.join([u'{0}{1}{2}{3}'.format(sep, pre1, node_name, dmark)]+[self._prt(child, len(name), sep=schar, pre1=p1, pre2=p2) for child, p1, p2, schar in zip(children, plist1, plist2, slist)])

	def _rnode(self, root, name, hierarchy):	#pylint: disable=C0111,R0913,R0914
		self._exh.ex_add(name='hierarchy_cannot_be_deleted', extype=RuntimeError, exmsg='Hierarchy *[node_name]* cannot be deleted')
		self._exh.ex_add(name='inconsistency_deleting_hierarchy', extype=RuntimeError, exmsg='Inconsitency when deleting hierarchy')
		suffix = name[len(root):]
		new_suffix = suffix.replace('.'+hierarchy, '').replace('..', '.')
		new_name = root+new_suffix
		if new_name != name:
			if not self.in_tree(new_name):
				self._db[new_name] = copy.deepcopy(self._db[name])
				self._db[self._db[name]['parent']]['children'] = sorted(list(set([child for child in self._db[self._db[name]['parent']]['children'] if child != name]+[new_name])))
			else:
				self._exh.raise_exception_if(name='hierarchy_cannot_be_deleted', condition=self._db[name]['data'], edata={'field':'hierarchy', 'value':hierarchy})
				if self._db[name]['parent'] == new_name:
					self._db[self._db[name]['parent']]['children'] = sorted(list(set([child for child in self._db[self._db[name]['parent']]['children'] if child != name])))
				new_children = sorted(self._db[new_name]['children']+self._db[name]['children'])
				self._exh.raise_exception_if(name='inconsistency_deleting_hierarchy', condition=len(new_children) != len(set(new_children)))
				self._db[new_name]['children'] = new_children
			for child in self.get_children(name):
				self._db[child]['parent'] = new_name
			del self._db[name]
		for child in self.get_children(new_name):
			self._rnode(root, child, hierarchy)

	def _set_root_name(self, name):	#pylint: disable=C0111
		self._root = name

	def _split_node_name(self, name, root_name=None):	#pylint: disable=C0111,R0201
		return [element.strip() for element in name.strip().split('.')][0 if not root_name else self._root_hierarchy_length:]

	@putil.check.check_argument(putil.check.PolymorphicType([{'name':NodeName(), 'data':putil.check.Any()}, putil.check.ArbitraryLengthList({'name':NodeName(), 'data':putil.check.Any()})]))
	def add(self, nodes):
		"""
		Add nodes to tree

		:param	nodes: Node(s) to add. Each dictionary must contain exactly two keys:

		 * **name** (*string*) node name

		 * **data** (*any*) node data.

		 If there are several list items in **nodes** with the same node name the resulting node data is a list with items corresponding to the data of each entry in **nodes** with the same node name, in their order \
		 of appearance, in addition to any existing node data if the node is already present in the tree.

		 The node data should be an empty list to create a node without data, for example: `{'node':'a.b.c', 'data':list()}`

		:type	nodes: dictionary or list of dictionaries

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('add')) ]]]

		:raises:
		 * TypeError (Argument `nodes` is of the wrong type)

		 * ValueError (Illegal node name: *[node_name]*)

		 * Same as :py:meth:`putil.tree.Tree.in_tree`

		.. [[[end]]]


		For example:

			>>> import putil.tree
			>>> tobj = putil.tree.Tree()
			>>> tobj.add([
			...		{'name':'root.branch1', 'data':5},
			...		{'name':'root.branch1', 'data':7},
			...		{'name':'root.branch2', 'data':list()},
			...		{'name':'root.branch1.leaf1', 'data':list()},
			...		{'name':'root.branch1.leaf1.subleaf1', 'data':333},
			...		{'name':'root.branch1.leaf2', 'data':'Hello world!'},
			...		{'name':'root.branch1.leaf2.subleaf2', 'data':list()},
			... ])
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.get_data('root.branch1')
			[5, 7]

		"""
		self._exh.ex_add(name='illegal_node_name', extype=ValueError, exmsg='Illegal node name: *[node_name]*')
		nodes = nodes if isinstance(nodes, list) else [nodes]
		# Create root node (if needed)
		if not self.root_name:
			self._set_root_name(nodes[0]['name'].split('.')[0].strip())
			self._db[self.root_name] = {'parent':'', 'children':list(), 'data':list()}
			self._root_hierarchy_length = len(self.root_name.split('.'))
		# Process new data
		for node_dict in nodes:
			name, data = node_dict['name'], node_dict['data']
			if name not in self._db:
				# Validate node name (root of new node same as tree root)
				hierarchy = self._split_node_name(name)
				self._exh.raise_exception_if(name='illegal_node_name', condition=not name.startswith(self.root_name+'.'), edata={'field':'node_name', 'value':name})
				# Create intermediate nodes if node not in tree
				hierarchy = self._split_node_name(name, self.root_name)
				node_tree = [self.root_name+'.'+('.'.join(hierarchy[:num+1])) for num in range(len(hierarchy))]
				for parent, child in [(child[:child.rfind('.')], child) for child in node_tree if child not in self._db]:
					self._db[child] = {'parent':parent, 'children':list(), 'data':list()}
					self._db[parent]['children'] = sorted(list(set(self._db[parent]['children']+[child])))
			self._db[name]['data'] += (data if isinstance(data, list) and data else (list() if isinstance(data, list) else [data]))

	@putil.check.check_argument(NodeName())
	def collapse(self, name):
		"""
		Collapses hierarchy. Nodes that have a single child and no data are combined with their child as a single tree node

		:param	name: Root of the sub-tree to collapse
		:type	name: string

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('collapse')) ]]]

		:raises:
		 * RuntimeError (Node *[node_name]* not in tree)

		 * TypeError (Argument `name` is of the wrong type)

		.. [[[end]]]


		Using the same example tree created in :py:meth:`putil.tree.Tree.add`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.collapse('branch1')
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1.subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2

		``root.branch1.leaf1`` is collapsed because it only has one child (``root.branch1.leaf1.subleaf1``) and no data; ``root.branch1.leaf2`` is not collapsed because although it has one child (``root.branch1.leaf2.subleaf2``) \
		it does have data associated with it, *'Hello world!'*
		"""
		self._node_in_tree(name)
		for child in copy.deepcopy(self._db[name]['children']):
			self._collapse_node(child)

	@putil.check.check_arguments({'source_node':NodeName(), 'dest_node':NodeName()})
	def copy_subtree(self, source_node, dest_node):
		"""
		Copy a sub-tree from one sub-node to another. Data is added if some nodes of the source sub-treeexist in the destination sub-tree

		:param	source_name: Root node of the sub-tree to copy from
		:type	source_name: string
		:param	dest_name: Root node of the sub-tree to copy to
		:type	dest_name: string

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('copy_subtree')) ]]]

		:raises:
		 * RuntimeError (Illegal root in destination node)

		 * TypeError (Argument `dest_node` is of the wrong type)

		 * TypeError (Argument `source_node` is of the wrong type)

		 * Same as :py:meth:`putil.tree.Tree.add`

		 * Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]


		Using the same example tree created in :py:meth:`putil.tree.Tree.add`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.copy_subtree('root.branch1', 'root.branch3')
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1.subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			├branch2
			└branch3 (*)
			 ├leaf1
			 │└subleaf1 (*)
			 └leaf2 (*)
			  └subleaf2

		"""
		self._exh.ex_add(name='illegal_dest_node', extype=RuntimeError, exmsg='Illegal root in destination node')
		self._node_in_tree(source_node)
		self._exh.raise_exception_if(name='illegal_dest_node', condition=not dest_node.startswith(self.root_name+'.'))
		for node in self.get_subtree(source_node):
			self.add({'name':node.replace(source_node, dest_node, 1), 'data':self.get_data(node)})

	@putil.check.check_argument(putil.check.PolymorphicType([NodeName(), putil.check.ArbitraryLengthList(NodeName())]))
	def delete(self, nodes):
		"""
		Delete nodes (and their sub-trees) from tree

		:param	nodes: Node(s) to delete
		:type	nodes: string or list of strings

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('delete')) ]]]

		:raises:
		 * TypeError (Argument `nodes` is of the wrong type)

		 * Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.delete(['root.branch1.leaf1', 'root.branch2'])
			>>> print str(tobj)
			root
			└branch1 (*)
			 └leaf2 (*)
			  └subleaf2

		"""
		nodes = nodes if isinstance(nodes, list) else [nodes]
		for parent, node in [(self._db[node]['parent'], node) for node in nodes if self._node_in_tree(node)]:
			# Delete link to parent (if not root node)
			del_list = self.get_subtree(node)
			if parent:
				self._db[parent]['children'].remove(node)
			# Delete children (sub-tree)
			for child in del_list:
				del self._db[child]
			if not len(self._db):
				self._root = None
				self._root_hierarchy_length = None

	@putil.check.check_argument(NodeName())
	def flatten_subtree(self, name):
		"""
		Flatten sub-tree below a particular node if the node contains no data

		:param	name: Ending hierarchy node whose sub-trees are to be flattened
		:type	name: string

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('delete')) ]]]

		:raises:
		 * TypeError (Argument `nodes` is of the wrong type)

		 * Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add`:

			>>> tobj.add([{'name':'root.branch1.leaf1.subleaf2', 'data':list()},
			...           {'name':'root.branch2.leaf1', 'data':'loren ipsum'},
			...           {'name':'root.branch2.leaf1.another_subleaf1', 'data':list()},
			...           {'name':'root.branch2.leaf1.another_subleaf2', 'data':list()}
			...         ])
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││├subleaf1 (*)
			││└subleaf2
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			 └leaf1
			  ├another_subleaf1
			  └another_subleaf2
			>>> tobj.flatten_subtree('root1.branch1.leaf1')
			root
			├branch1 (*)
			│├leaf1.subleaf1 (*)
			│├leaf1.subleaf2
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			 └leaf1 (*)
			  ├another_subleaf1
			  └another_subleaf2
			>>> tobj.flatten_subtree('root1.branch2.leaf1')
			root
			├branch1 (*)
			│├leaf1.subleaf1 (*)
			│├leaf1.subleaf2
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			 └leaf1 (*)
			  ├another_subleaf1
			  └another_subleaf2

		"""
		self._node_in_tree(name)
		if (self._db[name]['parent']) and (not self._db[name]['data']):
			parent = self._db[name]['parent']
			children = self._db[name]['children']
			for child in children:
				self._db[child]['parent'] = parent
			self._db[parent]['children'].remove(name)
			self._db[parent]['children'] = sorted(self._db[parent]['children']+children)
			del self._db[name]

	@putil.check.check_argument(NodeName())
	def get_children(self, name):	#pylint: disable=C0111
		"""
		Return children node names of a node

		:param	name: Node name
		:type	name: string
		:rtype	data: list of strings

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_children')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return sorted(self._db[name]['children'])

	@putil.check.check_argument(NodeName())
	def get_data(self, name):	#pylint: disable=C0111
		"""
		Return node data

		:param	name: Node name
		:type	name: string
		:rtype	data: any type or list of objects of any type

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_data')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[name]['data']

	@putil.check.check_argument(NodeName())
	def get_leafs(self, name):	#pylint: disable=C0111
		"""
		Return sub-tree leaf node(s)

		:param	name: Sub-tree root node name
		:type	name: string
		:rtype	data: list

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_leafs')) ]]]
		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return [node for node in self.get_subtree(name) if self.is_leaf(node)]


	@putil.check.check_argument(NodeName())
	def get_node(self, name):	#pylint: disable=C0111
		"""
		Get tree node structure. The structure is a dictionary with the following keys:

		 * **parent** (*string*) Parent node name, *''* if node is the root node

		 * **children** (*list*) Children node names, empty list if node is a leaf

		 * **data** (*list*) Node data, empty list if node contains no data

		:param	name: Node name
		:type	name: string
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[name]

	@putil.check.check_argument(NodeName())
	def get_node_children(self, name):	#pylint: disable=C0111
		"""
		Return list of children structures of a node. See :py:meth:`putil.tree.Tree.get_node()` for details about structure.

		:param	name: Child node name
		:type	name: string
		:rtype: list

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node_parent')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return [self.get_node(child) for child in self.get_children(name)]

	@putil.check.check_argument(NodeName())
	def get_node_parent(self, name):	#pylint: disable=C0111
		"""
		Return parent structure of a node. See :py:meth:`putil.tree.Tree.get_node()` for details about structure

		:param	name: Child node name
		:type	name: string
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node_parent')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[self._db[name]['parent']] if not self.is_root(name) else dict()

	def get_subtree(self, name):
		return [name]+[node for child in self.get_children(name) for node in self.get_subtree(child)]

	@putil.check.check_argument(NodeName())
	def in_tree(self, name):
		"""
		Return *True* if node name is in the tree, *False* otherwise

		:param	name: Node name to search for
		:type	name: string
		:rtype	data: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('in_tree')) ]]]

		:raises: TypeError (Argument `name` is of the wrong type)

		.. [[[end]]]
		"""
		return name in self._db

	@putil.check.check_argument(NodeName())
	def is_root(self, name):	#pylint: disable=C0111
		"""
		Root node flag, *True* if node is the root node (node with no ancestors), *False* otherwise

		:param	name: Node name
		:type	name: string
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('is_root')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
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

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('is_leaf')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return not self._db[name]['children']

	@putil.check.check_argument(NodeName())
	def make_root(self, name):	#pylint: disable=C0111
		"""
		Makes a sub-node the root node of the tree. All nodes not belonging to the sub-tree are deleted

		:param	name: New root node name
		:type	name: string
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('make_root')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse`

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.make_root('root.branch1')
			>>> print str(tobj)
			root.branch1 (*)
			├leaf1
			│└subleaf1 (*)
			└leaf2 (*)
			 └subleaf2

		"""
		if (name != self.root_name) and (self._node_in_tree(name)):
			for key in [node for node in self.nodes if node.find(name) != 0]:
				del self._db[key]
			self._db[name]['parent'] = ''
			self._root = name
			self._root_hierarchy_length = len(self.root_name.split('.'))

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

	@putil.check.check_argument(NodeName())
	def remove_prefix(self, prefix):
		self._exh.ex_add(name='illegal_prefix', extype=ValueError, exmsg='Illegal prefix')
		index = self.root_name.find(prefix)
		self._exh.raise_exception_if(name='illegal_prefix', condition=(index != 0) or (self.in_tree(prefix)))
		cstart = len(prefix)+1
		ndb = dict()
		for key in self._db.keys():
			new_key = key[cstart:]
			self._db[key]['parent'] = self._db[key]['parent'] if not self._db[key]['parent'] else self._db[key]['parent'][cstart:]
			self._db[key]['children'] = sorted([child[cstart:] for child in self._db[key]['children']])
			ndb[new_key] = copy.deepcopy(self._db[key])
			del self._db[key]
		self._db = ndb
		self._set_root_name(self.root_name[cstart:])
		self._root_hierarchy_length = len(self.root_name.split('.'))

	@putil.check.check_argument(NodeName())
	def rename_node(self, name, new_name):
		self._exh.ex_add(name='new_name_exists', extype=RuntimeError, exmsg='Node *[node_name]* already exists')
		self._exh.ex_add(name='illegal_new_name', extype=RuntimeError, exmsg='Argument `new_name` has an illegal root node')
		self._node_in_tree(name)
		self._exh.raise_exception_if(name='new_name_exists', condition=self.in_tree(new_name), edata={'field':'node_name', 'value':new_name})
		self._exh.raise_exception_if(name='illegal_new_name', condition=not new_name.startswith(self.root_name+'.'))
		self.copy_subtree(name, new_name)
		self.delete(name)

	# Managed attributes
	nodes = property(_get_nodes, None, None, doc='Tree nodes')
	"""
	Name of all tree nodes, *None* if an empty tree

	:rtype: list or None
	"""	#pylint: disable=W0105

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
