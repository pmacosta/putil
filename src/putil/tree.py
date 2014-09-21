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
tobj = putil.tree.Tree()
tobj.add_nodes([
	{'name':'dummy.root.branch1', 'data':list()},
	{'name':'dummy.root.branch2', 'data':list()},
	{'name':'dummy.root.branch1.leaf1', 'data':list()},
	{'name':'dummy.root.branch1.leaf1.subleaf1', 'data':333},
	{'name':'dummy.root.branch1.leaf2', 'data':'Hello world!'},
	{'name':'dummy.root.branch1.leaf2.subleaf2', 'data':list()},
])
tobj.collapse_subtree('dummy.root.branch1')
tobj.copy_subtree('dummy.root.branch1', 'dummy.root.branch3')
tobj.delete_subtree('dummy.root.branch2')
tobj.flatten_subtree('dummy.root.branch1')
tobj.get_children('dummy.root')
tobj.get_data('dummy.root')
tobj.get_leafs('dummy.root')
tobj.get_node('dummy.root')
tobj.get_node_children('dummy.root')
tobj.get_node_parent('dummy.root.branch1.leaf1.subleaf1')
tobj.get_subtree('dummy.root.branch3')
tobj.is_root('dummy.root')
tobj.in_tree('dummy.root')
tobj.is_leaf('dummy.root')
tobj.make_root('dummy.root.branch3')
tobj.print_node('dummy.root.branch3')
tobj.rename_node('dummy.root.branch3', 'root')
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
		return '' if not self._db else self._prt(name=self.root_name, lparent=-1, sep='', pre1='', pre2='').encode('utf-8')

	def _collapse_node(self, name):
		""" Collapse a sub-tree """
		oname = name
		children = self._db[name]['children']
		data = self._db[name]['data']
		del_list = list()
		while (len(children) == 1) and (not data):
			del_list.append(name)
			name = children[0]
			children = self._db[name]['children']
			data = self._db[name]['data']
		parent = self._db[oname]['parent']
		self._db[name]['parent'] = parent
		self._db[parent]['children'].remove(oname)
		self._db[parent]['children'] = sorted(self._db[parent]['children']+[name])
		for node in del_list:
			self._del_node(node)
		for name in copy.copy(children):
			self._collapse_node(name)

	def _create_node(self, name, parent, children, data):
		""" Create new tree node """
		self._db[name] = {'parent':parent, 'children':children, 'data':data}

	def _create_intermediate_nodes(self, name):
		""" Create intermediate nodes if hierarchy does not exist """
		hierarchy = self._split_node_name(name, self.root_name)
		node_tree = [self.root_name+'.'+('.'.join(hierarchy[:num+1])) for num in range(len(hierarchy))]
		for parent, child in [(child[:child.rfind('.')], child) for child in node_tree if child not in self._db]:
			self._db[child] = {'parent':parent, 'children':list(), 'data':list()}
			self._db[parent]['children'] = sorted(self._db[parent]['children']+[child])

	def _delete_subtree(self, nodes):
		""" Delete subtree private method (no argument validation and usage of getter/setter private methods for speed) """
		nodes = nodes if isinstance(nodes, list) else [nodes]
		for parent, node in [(self._db[node]['parent'], node) for node in nodes if self._node_in_tree(node)]:
			# Delete link to parent (if not root node)
			del_list = self._get_subtree(node)
			if parent:
				self._db[parent]['children'].remove(node)
			# Delete children (sub-tree)
			for child in del_list:
				del self._db[child]
			if self._empty_tree():
				self._root = None
				self._root_hierarchy_length = None

	def _del_node(self, name):
		""" Delete tree node """
		del self._db[name]

	def _empty_tree(self):
		""" Tests whether the object (tree) has any nodes/data """
		return True if not self._db else False

	def _get_children(self, name):
		return self._db[name]['children']

	def _get_data(self, name):
		return self._db[name]['data']

	def _get_nodes(self):	#pylint: disable=C0111
		return None if not self._db else sorted(self._db.keys())

	def _get_root_name(self):	#pylint: disable=C0111
		return self._root

	def _get_root_node(self):	#pylint: disable=C0111
		return None if not self.root_name else self._db[self.root_name]

	def _get_subtree(self, name):
		return [name]+[node for child in self._db[name]['children'] for node in self._get_subtree(child)]

	def _get_parent(self, name):
		return self._db[name]['parent']

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

	def _rename_node(self, name, new_name):
		""" Rename node private method (no argument validation and usage of getter/setter private methods for speed) """
		# Update parent
		if not self.is_root(name):
			parent = self._db[name]['parent']
			self._db[parent]['children'].remove(name)
			self._db[parent]['children'] = sorted(self._db[parent]['children']+[new_name])
		# Update children
		for key in self._get_subtree(name) if name != self.root_name else self.nodes:
			new_key = key.replace(name, new_name, 1)
			new_parent = self._db[key]['parent'] if key == name else self._db[key]['parent'].replace(name, new_name, 1)
			self._db[new_key] = {'parent':new_parent, 'children':[child.replace(name, new_name, 1) for child in self._db[key]['children']], 'data':copy.deepcopy(self._db[key]['data'])}
			del self._db[key]
		if name == self.root_name:
			self._root = new_name
			self._root_hierarchy_length = len(self.root_name.split('.'))


	def _set_children(self, name, children):
		self._db[name]['children'] = sorted(list(set(children)))

	def _set_data(self, name, data):
		self._db[name]['data'] = data

	def _set_root_name(self, name):	#pylint: disable=C0111
		self._root = name

	def _set_parent(self, name, parent):
		self._db[name]['parent'] = parent

	def _split_node_name(self, name, root_name=None):	#pylint: disable=C0111,R0201
		return [element.strip() for element in name.strip().split('.')][0 if not root_name else self._root_hierarchy_length:]

	@putil.check.check_argument(putil.check.PolymorphicType([{'name':NodeName(), 'data':putil.check.Any()}, putil.check.ArbitraryLengthList({'name':NodeName(), 'data':putil.check.Any()})]))
	def add_nodes(self, nodes):
		"""
		Add nodes to tree

		:param	nodes: Node(s) to add. Each dictionary must contain exactly two keys:

		 * **name** (*NodeName*) Node name. See `NodeName`_ pseudo-type specification

		 * **data** (*any*) node data.

		 If there are several list items in **nodes** with the same node name the resulting node data is a list with items corresponding to the data of each entry in **nodes** with the same node name, in their order \
		 of appearance, in addition to any existing node data if the node is already present in the tree.

		 The node data should be an empty list to create a node without data, for example: `{'node':'a.b.c', 'data':list()}`

		:type	nodes: dictionary or list of dictionaries

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('add')) ]]]
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
			self._root_hierarchy_length = len(self.root_name.split('.'))
			self._create_node(name=self.root_name, parent='', children=list(), data=list())
		# Process new data
		for node_dict in nodes:
			name, data = node_dict['name'], node_dict['data']
			if name not in self._db:
				# Validate node name (root of new node same as tree root)
				self._exh.raise_exception_if(name='illegal_node_name', condition=not name.startswith(self.root_name+'.'), edata={'field':'node_name', 'value':name})
				self._create_intermediate_nodes(name)
			self._db[name]['data'] += copy.deepcopy(data if isinstance(data, list) and data else (list() if isinstance(data, list) else [data]))

	@putil.check.check_argument(NodeName())
	def collapse_subtree(self, name):
		"""
		Collapses hierarchy. Nodes that have a single child and no data are combined with their child as a single tree node

		:param	name: Root of the sub-tree to collapse. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('collapse')) ]]]
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
		for child in copy.copy(self._db[name]['children']):
			self._collapse_node(child)

	@putil.check.check_arguments({'source_node':NodeName(), 'dest_node':NodeName()})
	def copy_subtree(self, source_node, dest_node):
		"""
		Copy a sub-tree from one sub-node to another. Data is added if some nodes of the source sub-treeexist in the destination sub-tree

		:param	source_name: Root node of the sub-tree to copy from. See `NodeName`_ pseudo-type specification
		:type	source_name: NodeName
		:param	dest_name: Root node of the sub-tree to copy to. See `NodeName`_ pseudo-type specification
		:type	dest_name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('copy_subtree')) ]]]

		:raises:
		 * RuntimeError (Illegal root in destination node)

		 * RuntimeError (Node *[node_name]* not in tree)

		 * TypeError (Argument `dest_node` is of the wrong type)

		 * TypeError (Argument `source_node` is of the wrong type)

		 * ValueError (Argument `dest_node` is not a valid node name)

		 * ValueError (Argument `source_node` is not a valid node name)

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
			│├leaf1
			││└subleaf1 (*)
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
		for node in self._get_subtree(source_node):
			self._db[node.replace(source_node, dest_node, 1)] = {'parent':self._db[node]['parent'].replace(source_node, dest_node, 1),
														         'children':[child.replace(source_node, dest_node, 1) for child in self._db[node]['children']],
														         'data':copy.deepcopy(self._db[node]['data'])}
		self._create_intermediate_nodes(dest_node)
		parent = '.'.join(dest_node.split('.')[:-1])
		self._db[dest_node]['parent'] = parent
		self._db[parent]['children'] = sorted(self._db[parent]['children']+[dest_node])

	@putil.check.check_argument(putil.check.PolymorphicType([NodeName(), putil.check.ArbitraryLengthList(NodeName())]))
	def delete_subtree(self, nodes):
		"""
		Delete nodes (and their sub-trees) from tree

		:param	nodes: Node(s) to delete. See `NodeName`_ pseudo-type specification
		:type	nodes: NodeName or list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('delete')) ]]]
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
		self._delete_subtree(nodes)

	@putil.check.check_argument(NodeName())
	def flatten_subtree(self, name):
		"""
		Flatten sub-tree below a particular node if the node contains no data

		:param	name: Ending hierarchy node whose sub-trees are to be flattened. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('flatten_subtree')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

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
			>>> tobj.flatten_subtree('root.branch1.leaf1')
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
			>>> tobj.flatten_subtree('root.branch2.leaf1')
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
		parent = self._db[name]['parent']
		if (parent) and (not self._db[name]['data']):
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

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_children')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return sorted(self._db[name]['children'])

	@putil.check.check_argument(NodeName())
	def get_data(self, name):	#pylint: disable=C0111
		"""
		Return node data

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeNames
		:rtype: any type or list of objects of any type

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_data')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[name]['data']

	@putil.check.check_argument(NodeName())
	def get_leafs(self, name):	#pylint: disable=C0111
		"""
		Return sub-tree leaf node(s)

		:param	name: Sub-tree root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_leafs')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return [node for node in self._get_subtree(name) if self.is_leaf(node)]


	@putil.check.check_argument(NodeName())
	def get_node(self, name):	#pylint: disable=C0111
		"""
		Get tree node structure. The structure is a dictionary with the following keys:

		 * **parent** (*NodeName*) Parent node name, *''* if node is the root node. See `NodeName`_ pseudo-type specification

		 * **children** (*list of NodeNames*) Children node names, empty list if node is a leaf. See `NodeName`_ pseudo-type specification

		 * **data** (*list*) Node data, empty list if node contains no data

		:param	name: Node name
		:type	name: string
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[name]

	@putil.check.check_argument(NodeName())
	def get_node_children(self, name):	#pylint: disable=C0111
		"""
		Return list of children structures of a node. See :py:meth:`putil.tree.Tree.get_node()` for details about structure.

		:param	name: Child node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node_children')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return [self._db[child] for child in self._db[name]['children']]

	@putil.check.check_argument(NodeName())
	def get_node_parent(self, name):	#pylint: disable=C0111
		"""
		Return parent structure of a node. See :py:meth:`putil.tree.Tree.get_node()` for details about structure

		:param	name: Child node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_node_parent')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return self._db[self._db[name]['parent']] if not self.is_root(name) else dict()

	@putil.check.check_argument(NodeName())
	def get_subtree(self, name):
		"""
		Return all node names in a sub-tree

		:param	name: Sub-tree root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('get_subtree')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

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
			>>> tobj.get_subtree('root.branch1')
			['root.branch1', 'root.branch1.leaf1', 'root.branch1.leaf1.subleaf1', 'root.branch1.leaf2', 'root.branch1.leaf2.subleaf2']

		"""
		self._node_in_tree(name)
		return self._get_subtree(name)

	@putil.check.check_argument(NodeName())
	def is_root(self, name):	#pylint: disable=C0111
		"""
		Root node flag, *True* if node is the root node (node with no ancestors), *False* otherwise

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('is_root')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return not self._db[name]['parent']

	@putil.check.check_argument(NodeName())
	def in_tree(self, name):
		"""
		Return *True* if node name is in the tree, *False* otherwise

		:param	name: Node name to search for. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype	data: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('in_tree')) ]]]

		:raises:
		 * TypeError (Argument `name` is of the wrong type)

		 * ValueError (Argument `name` is not a valid node name)

		.. [[[end]]]
		"""
		return name in self._db

	@putil.check.check_argument(NodeName())
	def is_leaf(self, name):	#pylint: disable=C0111
		"""
		Leaf node flag, *True* if node is a leaf node (node with no children), *False* otherwise

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('is_leaf')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		return not self._db[name]['children']

	@putil.check.check_argument(NodeName())
	def make_root(self, name):	#pylint: disable=C0111
		"""
		Makes a sub-node the root node of the tree. All nodes not belonging to the sub-tree are deleted

		:param	name: New root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('make_root')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

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
		Prints node information (parent, children and data)

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('print_node')) ]]]

		:raises: Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		.. [[[end]]]
		"""
		self._node_in_tree(name)
		node = self._db[name]
		children = [self._split_node_name(child)[-1] for child in node['children']] if node['children'] else node['children']
		data = node['data'][0] if node['data'] and (len(node['data']) == 1) else node['data']
		return 'Name: {0}\nParent: {1}\nChildren: {2}\nData: {3}'.format(name, node['parent'] if node['parent'] else None, ', '.join(children) if children else None, data if data else None)

	@putil.check.check_arguments({'name':NodeName(), 'new_name':NodeName()})
	def rename_node(self, name, new_name):
		"""
		Rename a tree node. It is typical to have a root node name with more than one hierarchy level after using :py:meth:`putil.tree.Tree.make_root`. In this instance the root node *can* be \
		renamed as long as the new root name has the same or less hierarchy levels as the old root name.

		:param	name: Node name to rename. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_doc_for_member('rename_node')) ]]]

		:raises:
		 * RuntimeError (Argument `new_name` has an illegal root node)

		 * RuntimeError (Argument `new_name` is an illegal root node name)

		 * RuntimeError (Node *[node_name]* already exists)

		 * TypeError (Argument `new_name` is of the wrong type)

		 * ValueError (Argument `new_name` is not a valid node name)

		 * Same as :py:meth:`putil.tree.Tree.collapse_subtree`

		 * Same as :py:meth:`putil.tree.Tree.in_tree`

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
			>>> tobj.rename_node('root.branch1.leaf1', 'root.branch1.mapleleaf1')
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf2 (*)
			││└subleaf2
			│└mapleleaf1
			│ └subleaf1 (*)
			└branch2

		"""
		self._exh.ex_add(name='new_name_exists', extype=RuntimeError, exmsg='Node *[node_name]* already exists')
		self._exh.ex_add(name='illegal_new_name', extype=RuntimeError, exmsg='Argument `new_name` has an illegal root node')
		self._exh.ex_add(name='illegal_new_root_name', extype=RuntimeError, exmsg='Argument `new_name` is an illegal root node name')
		self._node_in_tree(name)
		self._exh.raise_exception_if(name='new_name_exists', condition=self.in_tree(new_name) and (name != self.root_name), edata={'field':'node_name', 'value':new_name})
		self._exh.raise_exception_if(name='illegal_new_name', condition=(name.split('.')[:-1] != new_name.split('.')[:-1]) and (name != self.root_name))
		old_hierarchy_length = len(name.split('.'))
		new_hierarchy_length = len(new_name.split('.'))
		self._exh.raise_exception_if(name='illegal_new_root_name', condition=(name == self.root_name) and (old_hierarchy_length < new_hierarchy_length))
		self._rename_node(name, new_name)

	# Managed attributes
	nodes = property(_get_nodes, None, None, doc='Tree nodes')
	"""
	Name of all tree nodes, *None* if an empty tree. See `NodeName`_ pseudo-type specification

	:rtype: list of NodeNames or None
	"""	#pylint: disable=W0105

	root_node = property(_get_root_node, None, None, doc='Tree root node')
	"""
	Tree root node or *None* if :py:class:`putil.tree.Tree()` object has no nodes. See :py:meth:`putil.tree.Tree.get_node()` for details about returned dictionary.

	:rtype: dictionary or None
	"""	#pylint: disable=W0105

	root_name = property(_get_root_name, None, None, doc='Tree root node name')
	"""
	Tree root node name, *None* if :py:class:`putil.tree.Tree()` object has no nodes. See `NodeName`_ pseudo-type specification

	:rtype: NodeName or None
	"""	#pylint: disable=W0105
