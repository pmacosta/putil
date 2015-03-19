# -*- coding: utf-8 -*-
# tree.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import itertools, copy

import putil.exh


###
# Exception tracing initialization code
###
"""
[[[cog
import trace_ex_tree
exobj_tree = trace_ex_tree.trace_module(no_print=True)
]]]
[[[end]]]
"""	#pylint: disable=W0105


###
# Classes
###
class Tree(object):	#pylint: disable=R0903,R0902
	"""
	Provides basic `trie <http://wikipedia.org/wiki/Trie>`_ (radix tree) functionality

	:param	node_separator: Single character used to separate nodes in the tree
	:type	node_separator: string
	:rtype: :py:class:`putil.tree.Tree` object

	.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for putil.tree.Tree.__init__

	:raises: RuntimeError (Argument `node_separator` is not valid)

	.. [[[end]]]
	"""
	def __init__(self, node_separator='.'):	#pylint: disable=R0913
		self._db = dict()
		self._root = None
		self._root_hierarchy_length = None
		self._vertical = unichr(0x2502)
		self._vertical_and_right = unichr(0x251C)
		self._up_and_right = unichr(0x2514)
		self._exh = putil.exh.get_exh_obj() if putil.exh.get_exh_obj() else putil.exh.ExHandle()
		self._exh.add_exception(exname='illegal_node_separator', extype=RuntimeError, exmsg='Argument `node_separator` is not valid')
		self._exh.raise_exception_if(exname='illegal_node_separator', condition=(not isinstance(node_separator, str)) or (isinstance(node_separator, str) and len(node_separator) != 1))
		self._node_separator = node_separator

	def __copy__(self, memodict=None):
		memodict = dict() if memodict is None else memodict
		cobj = Tree(self.node_separator)
		cobj._db = copy.deepcopy(self._db, memodict)	#pylint: disable=W0212
		cobj._root = self._root
		cobj._root_hierarchy_length = self._root_hierarchy_length
		cobj._exh = self._exh
		return cobj

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

	def _collapse_subtree(self, name, recursive=True):
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
		if parent:
			self._db[parent]['children'].remove(oname)
			self._db[parent]['children'] = sorted(self._db[parent]['children']+[name])
		else:
			self._root = name
			self._root_hierarchy_length = len(self.root_name.split(self._node_separator))
		for node in del_list:
			self._del_node(node)
		if recursive:
			for name in copy.copy(children):
				self._collapse_subtree(name)

	def _create_node(self, name, parent, children, data):
		""" Create new tree node """
		self._db[name] = {'parent':parent, 'children':children, 'data':data}

	def _create_intermediate_nodes(self, name):
		""" Create intermediate nodes if hierarchy does not exist """
		hierarchy = self._split_node_name(name, self.root_name)
		node_tree = [self.root_name+self._node_separator+(self._node_separator.join(hierarchy[:num+1])) for num in xrange(len(hierarchy))]
		for parent, child in [(child[:child.rfind(self._node_separator)], child) for child in node_tree if child not in self._db]:
			self._db[child] = {'parent':parent, 'children':list(), 'data':list()}
			self._db[parent]['children'] = sorted(self._db[parent]['children']+[child])

	def _delete_prefix(self, name):
		lname = len(name)+1
		self._root = self._root[lname:]
		self._root_hierarchy_length = len(self.root_name.split(self._node_separator))
		for key, value in self._db.items():
			value['parent'] = value['parent'][lname:] if value['parent'] else value['parent']
			value['children'] = [child[lname:] for child in value['children']]
			del self._db[key]
			self._db[key[lname:]] = value

	def _delete_subtree(self, nodes):
		""" Delete subtree private method (no argument validation and usage of getter/setter private methods for speed) """
		nodes = nodes if isinstance(nodes, list) else [nodes]
		for parent, node in [(self._db[node]['parent'], node) for node in nodes if self._node_name_in_tree(node)]:
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

	def _get_node_separator(self):	#pylint: disable=C0111
		return self._node_separator

	def _get_root_name(self):	#pylint: disable=C0111
		return self._root

	def _get_root_node(self):	#pylint: disable=C0111
		return None if not self.root_name else self._db[self.root_name]

	def _get_subtree(self, name):
		return [name]+[node for child in self._db[name]['children'] for node in self._get_subtree(child)]

	def _get_parent(self, name):
		return self._db[name]['parent']

	def _node_in_tree(self, name):	#pylint: disable=C0111
		self._exh.add_exception(exname='node_not_in_tree', extype=RuntimeError, exmsg='Node *[name]* not in tree')
		self._exh.raise_exception_if(exname='node_not_in_tree', condition=name not in self._db, edata={'field':'name', 'value':name})
		return True

	def _node_name_in_tree(self, name):	#pylint: disable=C0111
		self._exh.add_exception(exname='node_not_in_tree', extype=RuntimeError, exmsg='Node *[node_name]* not in tree')
		self._exh.raise_exception_if(exname='node_not_in_tree', condition=name not in self._db, edata={'field':'node_name', 'value':name})
		return True

	def _prt(self, name, lparent, sep, pre1, pre2):	#pylint: disable=C0111,R0913,R0914
		# Characters from http://www.unicode.org/charts/PDF/U2500.pdf
		nname = name[lparent+1:]
		children = self._db[name]['children']
		ncmu = len(children)-1
		plist1 = ncmu*[self._vertical_and_right]+[self._up_and_right]
		plist2 = ncmu*[self._vertical]+[' ']
		slist = (ncmu+1)*[sep+pre2]
		dmark = ' (*)' if self._db[name]['data'] else ''
		return '\n'.join([u'{0}{1}{2}{3}'.format(sep, pre1, nname, dmark)]+[self._prt(child, len(name), sep=schar, pre1=p1, pre2=p2) for child, p1, p2, schar in itertools.izip(children, plist1, plist2, slist)])

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
			self._root_hierarchy_length = len(self.root_name.split(self._node_separator))

	def _search_tree(self, name):
		""" Search_tree for nodes that contain a specific hierarchy name """
		return sorted([node for node in self._db if ('{0}{1}{0}'.format(self._node_separator, name) in node) or node.endswith('{0}{1}'.format(self._node_separator, name)) or \
		  node.startswith('{0}{1}'.format(name, self._node_separator)) or (name == node)])

	def _set_children(self, name, children):
		self._db[name]['children'] = sorted(list(set(children)))

	def _set_data(self, name, data):
		self._db[name]['data'] = data

	def _set_root_name(self, name):	#pylint: disable=C0111
		self._root = name

	def _set_parent(self, name, parent):
		self._db[name]['parent'] = parent

	def _split_node_name(self, name, root_name=None):	#pylint: disable=C0111,R0201
		return [element.strip() for element in name.strip().split(self._node_separator)][0 if not root_name else self._root_hierarchy_length:]

	def _validate_node_name(self, var_value):	#pylint: disable=R0201
		""" NodeName pseudo-type validation """
		var_values = var_value if isinstance(var_value, list) else [var_value]
		for var_value in var_values:
			if (not isinstance(var_value, str)) or (isinstance(var_value, str) and ((' ' in var_value) or any([element.strip() == '' for element in var_value.strip().split(self._node_separator)]))):
				return True
		return False

	def _validate_nodes_with_data(self, names):
		""" NodeWithData pseudo-type validation """
		self._exh.add_exception(exname='illegal_node_with_data', extype=RuntimeError, exmsg='Argument `nodes` is not valid')
		names = names if isinstance(names, list) else [names]
		self._exh.raise_exception_if(exname='illegal_node_with_data', condition=not names)
		for ndict in names:
			self._exh.raise_exception_if(exname='illegal_node_with_data', condition=(not isinstance(ndict, dict)) or (isinstance(ndict, dict) and (set(ndict.keys()) != set(['name', 'data']))))
			name = ndict['name']
			self._exh.raise_exception_if(exname='illegal_node_with_data',
								condition=(not isinstance(name, str)) or (isinstance(name, str) and ((' ' in name) or any([element.strip() == '' for element in name.strip().split(self._node_separator)]))))

	def add_nodes(self, nodes):
		"""
		Adds nodes to tree

		:param	nodes: Node(s) to add with associated data. If there are several list items in the argument with the same node name the resulting node data is a list with items corresponding to the data of each entry in \
		the argument with the same node name, in their order of appearance, in addition to any existing node data if the node is already present in the tree

		:type	nodes: NodesWithData

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.add_nodes

		:raises:
		 * RuntimeError (Argument `nodes` is not valid)

		 * ValueError (Illegal node name: *[node_name]*)

		.. [[[end]]]

		For example:

			>>> import putil.tree
			>>> tobj = putil.tree.Tree()
			>>> tobj.add_nodes([
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
		self._validate_nodes_with_data(nodes)
		self._exh.add_exception(exname='illegal_node_name', extype=ValueError, exmsg='Illegal node name: *[node_name]*')
		nodes = nodes if isinstance(nodes, list) else [nodes]
		# Create root node (if needed)
		if not self.root_name:
			self._set_root_name(nodes[0]['name'].split(self._node_separator)[0].strip())
			self._root_hierarchy_length = len(self.root_name.split(self._node_separator))
			self._create_node(name=self.root_name, parent='', children=list(), data=list())
		# Process new data
		for node_dict in nodes:
			name, data = node_dict['name'], node_dict['data']
			if name not in self._db:
				# Validate node name (root of new node same as tree root)
				self._exh.raise_exception_if(exname='illegal_node_name', condition=not name.startswith(self.root_name+self._node_separator), edata={'field':'node_name', 'value':name})
				self._create_intermediate_nodes(name)
			self._db[name]['data'] += copy.deepcopy(data if isinstance(data, list) and data else (list() if isinstance(data, list) else [data]))

	def collapse_subtree(self, name, recursive=True):
		"""
		Collapses a sub-tree; nodes that have a single child and no data are combined with their child as a single tree node

		:param	name: Root of the sub-tree to collapse. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:param	recursive: Flag that indicates whether the collapse operation should be performed on the whole sub-tree (True) or whether it should stop upon reaching the first node
		 where the collapsing condition is not satisfied (False)

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.collapse_subtree

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Argument `recursive` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.collapse_subtree('root.branch1')
			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1.subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2

		``root.branch1.leaf1`` is collapsed because it only has one child (``root.branch1.leaf1.subleaf1``) and no data; ``root.branch1.leaf2`` is not collapsed because although it has one child (``root.branch1.leaf2.subleaf2``) \
		it does have data associated with it, :code:`'Hello world!'`
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._exh.add_exception(exname='illegal_recursive', extype=RuntimeError, exmsg='Argument `recursive` is not valid')
		self._exh.raise_exception_if(exname='illegal_recursive', condition=not isinstance(recursive, bool))
		self._node_in_tree(name)
		self._collapse_subtree(name, recursive)

	def copy_subtree(self, source_node, dest_node):
		"""
		Copies a sub-tree from one sub-node to another. Data is added if some nodes of the source sub-tree exist in the destination sub-tree

		:param	source_name: Root node of the sub-tree to copy from. See `NodeName`_ pseudo-type specification
		:type	source_name: NodeName
		:param	dest_name: Root node of the sub-tree to copy to. See `NodeName`_ pseudo-type specification
		:type	dest_name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.copy_subtree

		:raises:
		 * RuntimeError (Argument `dest_node` is not valid)

		 * RuntimeError (Argument `source_node` is not valid)

		 * RuntimeError (Illegal root in destination node)

		 * RuntimeError (Node *[source_node]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

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
		self._exh.add_exception(exname='illegal_source_node', extype=RuntimeError, exmsg='Argument `source_node` is not valid')
		self._exh.add_exception(exname='source_node_not_in_tree', extype=RuntimeError, exmsg='Node *[source_node]* not in tree')
		self._exh.add_exception(exname='illegal_dest_node1', extype=RuntimeError, exmsg='Argument `dest_node` is not valid')
		self._exh.add_exception(exname='illegal_dest_node2', extype=RuntimeError, exmsg='Illegal root in destination node')
		self._exh.raise_exception_if(exname='illegal_source_node', condition=self._validate_node_name(source_node))
		self._exh.raise_exception_if(exname='illegal_dest_node1', condition=self._validate_node_name(dest_node))
		self._exh.raise_exception_if(exname='source_node_not_in_tree', condition=source_node not in self._db, edata={'field':'source_node', 'value':source_node})
		self._exh.raise_exception_if(exname='illegal_dest_node2', condition=not dest_node.startswith(self.root_name+self._node_separator))
		for node in self._get_subtree(source_node):
			self._db[node.replace(source_node, dest_node, 1)] = {'parent':self._db[node]['parent'].replace(source_node, dest_node, 1),
														         'children':[child.replace(source_node, dest_node, 1) for child in self._db[node]['children']],
														         'data':copy.deepcopy(self._db[node]['data'])}
		self._create_intermediate_nodes(dest_node)
		parent = self._node_separator.join(dest_node.split(self._node_separator)[:-1])
		self._db[dest_node]['parent'] = parent
		self._db[parent]['children'] = sorted(self._db[parent]['children']+[dest_node])

	def delete_prefix(self, name):
		"""
		Deletes hierarchy levels from all nodes in the tree

		:param	nodes: Prefix to delete. See `NodeName`_ pseudo-type specification
		:type	nodes: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.delete_prefix

		:raises:
		 * RuntimeError (Argument `name` is not a valid prefix)

		 * RuntimeError (Argument `name` is not valid)

		.. [[[end]]]

		For example:

			>>> tobj.add_nodes([{'name':'hello/world/root', 'data':list()},
			...                 {'name':'hello/world/root/anode', 'data':7},
			...                 {'name':'hello/world/root/bnode', 'data':list()},
			...                 {'name':'hello/world/root/cnode', 'data':list()},
			...                 {'name':'hello/world/root/bnode/anode', 'data':['a', 'b'. 'c']},
			...                 {'name':'hello/world/root/cnode/anode/leaf', 'data':True}
			...                ])
			>>> print str(tobj)
			hello/world/root
			├anode (*)
			├bnode
			│└anode (*)
			└cnode
			 └anode
			  └leaf (*)
			>>> tobj.delete_prefix('hello/world')
			>>> print str(tobj)
			root
			├anode (*)
			├bnode
			│└anode (*)
			└cnode
			 └anode
			  └leaf (*)
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.add_exception(exname='illegal_prefix', extype=RuntimeError, exmsg='Argument `name` is not a valid prefix')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._exh.raise_exception_if(exname='illegal_prefix', condition=(not self.root_name.startswith(name)) or (self.root_name == name))
		self._delete_prefix(name)

	def delete_subtree(self, nodes):
		"""
		Deletes nodes (and their sub-trees) from the tree

		:param	nodes: Node(s) to delete. See `NodeName`_ pseudo-type specification
		:type	nodes: NodeName or list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.delete_subtree

		:raises:
		 * RuntimeError (Argument `nodes` is not valid)

		 * RuntimeError (Node *[node_name]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

			>>> print str(tobj)
			root
			├branch1 (*)
			│├leaf1
			││└subleaf1 (*)
			│└leaf2 (*)
			│ └subleaf2
			└branch2
			>>> tobj.delete_subtree(['root.branch1.leaf1', 'root.branch2'])
			>>> print str(tobj)
			root
			└branch1 (*)
			 └leaf2 (*)
			  └subleaf2

		"""
		self._exh.add_exception(exname='illegal_nodes', extype=RuntimeError, exmsg='Argument `nodes` is not valid')
		self._exh.raise_exception_if(exname='illegal_nodes', condition=self._validate_node_name(nodes))
		self._delete_subtree(nodes)

	def flatten_subtree(self, name):
		"""
		Flattens sub-tree; nodes that have children and no data are merged with each child

		:param	name: Ending hierarchy node whose sub-trees are to be flattened. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.flatten_subtree

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

			>>> tobj.add_nodes([{'name':'root.branch1.leaf1.subleaf2', 'data':list()},
			...                 {'name':'root.branch2.leaf1', 'data':'loren ipsum'},
			...                 {'name':'root.branch2.leaf1.another_subleaf1', 'data':list()},
			...                 {'name':'root.branch2.leaf1.another_subleaf2', 'data':list()}
			...                ])
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
			>>> print str(tobj)
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
			>>> print str(tobj)
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
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		parent = self._db[name]['parent']
		if (parent) and (not self._db[name]['data']):
			children = self._db[name]['children']
			for child in children:
				self._db[child]['parent'] = parent
			self._db[parent]['children'].remove(name)
			self._db[parent]['children'] = sorted(self._db[parent]['children']+children)
			del self._db[name]

	def get_children(self, name):	#pylint: disable=C0111
		"""
		Gets the children node names of a node

		:param	name: Parent node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_children

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return sorted(self._db[name]['children'])

	def get_data(self, name):	#pylint: disable=C0111
		"""
		Gets the data associated with a node

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeNames
		:rtype: any type or list of objects of any type

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_data

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return self._db[name]['data']

	def get_leafs(self, name):	#pylint: disable=C0111
		"""
		Gets the sub-tree leaf node(s)

		:param	name: Sub-tree root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_leafs

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return [node for node in self._get_subtree(name) if self.is_leaf(node)]

	def get_node(self, name):	#pylint: disable=C0111
		"""
		Gets a tree node structure. The structure is a dictionary with the following keys:

		 * **parent** (*NodeName*) Parent node name, :code:`''` if the node is the root node. See `NodeName`_ pseudo-type specification

		 * **children** (*list of NodeNames*) Children node names, an empty list if node is a leaf. See `NodeName`_ pseudo-type specification

		 * **data** (*list*) Node data, an empty list if node contains no data

		:param	name: Node name
		:type	name: string
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_node

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return self._db[name]

	def get_node_children(self, name):	#pylint: disable=C0111
		"""
		Gets the list of children structures of a node. See :py:meth:`putil.tree.Tree.get_node` for details about the structure

		:param	name: Parent node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_node_children

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return [self._db[child] for child in self._db[name]['children']]

	def get_node_parent(self, name):	#pylint: disable=C0111
		"""
		Gets the parent structure of a node. See :py:meth:`putil.tree.Tree.get_node` for details about the structure

		:param	name: Child node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: dictionary

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_node_parent

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return self._db[self._db[name]['parent']] if not self.is_root(name) else dict()

	def get_subtree(self, name):
		"""
		Gets all node names in a sub-tree

		:param	name: Sub-tree root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: list of NodeNames

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.get_subtree

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

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
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return self._get_subtree(name)

	def is_root(self, name):	#pylint: disable=C0111
		"""
		Tests if a node is the root node (node with no ancestors)

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.is_root

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return not self._db[name]['parent']

	def in_tree(self, name):
		"""
		Tests if a node is in the tree

		:param	name: Node name to search for. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype	data: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.in_tree

		:raises: RuntimeError (Argument `name` is not valid)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		return name in self._db

	def is_leaf(self, name):	#pylint: disable=C0111
		"""
		Tests if a node is a leaf node (node with no children)

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName
		:rtype: boolean

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.is_leaf

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		return not self._db[name]['children']

	def make_root(self, name):	#pylint: disable=C0111
		"""
		Makes a sub-node the root node of the tree. All nodes not belonging to the sub-tree are deleted

		:param	name: New root node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.make_root

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

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
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		if (name != self.root_name) and (self._node_in_tree(name)):
			for key in [node for node in self.nodes if node.find(name) != 0]:
				del self._db[key]
			self._db[name]['parent'] = ''
			self._root = name
			self._root_hierarchy_length = len(self.root_name.split(self._node_separator))

	def print_node(self, name):	#pylint: disable=C0111
		"""
		Prints node information (parent, children and data)

		:param	name: Node name. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.print_node

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		.. [[[end]]]
		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._node_in_tree(name)
		node = self._db[name]
		children = [self._split_node_name(child)[-1] for child in node['children']] if node['children'] else node['children']
		data = node['data'][0] if node['data'] and (len(node['data']) == 1) else node['data']
		return 'Name: {0}\nParent: {1}\nChildren: {2}\nData: {3}'.format(name, node['parent'] if node['parent'] else None, ', '.join(children) if children else None, data if data else None)

	def rename_node(self, name, new_name):
		"""
		Renames a tree node. It is typical to have a root node name with more than one hierarchy level after using :py:meth:`putil.tree.Tree.make_root`. In this instance the root node *can* be \
		renamed as long as the new root name has the same or less hierarchy levels as the existing root name.

		:param	name: Node name to rename. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.rename_node

		:raises:
		 * RuntimeError (Argument `name` is not valid)

		 * RuntimeError (Argument `new_name` has an illegal root node)

		 * RuntimeError (Argument `new_name` is an illegal root node name)

		 * RuntimeError (Argument `new_name` is not valid)

		 * RuntimeError (Node *[name]* not in tree)

		 * RuntimeError (Node *[new_name]* already exists)

		.. [[[end]]]

		Using the same example tree created in :py:meth:`putil.tree.Tree.add_nodes`:

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
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.add_exception(exname='illegal_new_name1', extype=RuntimeError, exmsg='Argument `new_name` is not valid')
		self._exh.add_exception(exname='new_name_exists', extype=RuntimeError, exmsg='Node *[new_name]* already exists')
		self._exh.add_exception(exname='illegal_new_name2', extype=RuntimeError, exmsg='Argument `new_name` has an illegal root node')
		self._exh.add_exception(exname='illegal_new_root_name', extype=RuntimeError, exmsg='Argument `new_name` is an illegal root node name')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		self._exh.raise_exception_if(exname='illegal_new_name1', condition=self._validate_node_name(new_name))
		self._node_in_tree(name)
		self._exh.raise_exception_if(exname='new_name_exists', condition=self.in_tree(new_name) and (name != self.root_name), edata={'field':'new_name', 'value':new_name})
		self._exh.raise_exception_if(exname='illegal_new_name2', condition=(name.split(self._node_separator)[:-1] != new_name.split(self._node_separator)[:-1]) and (name != self.root_name))
		old_hierarchy_length = len(name.split(self._node_separator))
		new_hierarchy_length = len(new_name.split(self._node_separator))
		self._exh.raise_exception_if(exname='illegal_new_root_name', condition=(name == self.root_name) and (old_hierarchy_length < new_hierarchy_length))
		self._rename_node(name, new_name)

	def search_tree(self, name):
		"""
		Searches tree for all nodes of a specific name

		:param	name: Node name to search for. See `NodeName`_ pseudo-type specification
		:type	name: NodeName

		.. [[[cog cog.out(exobj_tree.get_sphinx_autodoc()) ]]]
		.. Auto-generated exceptions documentation for putil.tree.Tree.search_tree

		:raises: RuntimeError (Argument `name` is not valid)

		.. [[[end]]]

		For example:

			>>> tobj.add_nodes([{'name':'root', 'data':list()},
			...                 {'name':'root/anode', 'data':7},
			...                 {'name':'root/bnode', 'data':list()},
			...                 {'name':'root/cnode', 'data':list()},
			...                 {'name':'root/bnode/anode', 'data':['a', 'b'. 'c']},
			...                 {'name':'root/cnode/anode/leaf', 'data':True}
			...                ])
			>>> print str(tobj)
			root
			├anode (*)
			├bnode
			│└anode (*)
			└cnode
			 └anode
			  └leaf (*)
			>>> tobj.search_tree('anode')
			['root/anode', 'root/bnode/anode', 'root/cnode/anode', 'root/cnode/anode/leaf']

		"""
		self._exh.add_exception(exname='illegal_name', extype=RuntimeError, exmsg='Argument `name` is not valid')
		self._exh.raise_exception_if(exname='illegal_name', condition=self._validate_node_name(name))
		return self._search_tree(name)

	# Managed attributes
	nodes = property(_get_nodes, None, None, doc='Tree nodes')
	"""
	Gets the name of all tree nodes, :code:`None` if the tree is empty. See `NodeName`_ pseudo-type specification

	:rtype: list of NodeNames or None
	"""	#pylint: disable=W0105

	node_separator = property(_get_node_separator, None, None, doc='Node separator')
	"""
	Gets the node separator character

	:rtype: string
	"""	#pylint: disable=W0105

	root_node = property(_get_root_node, None, None, doc='Tree root node')
	"""
	Gets the tree root node structure or :code:`None` if :py:class:`putil.tree.Tree` object has no nodes. See :py:meth:`putil.tree.Tree.get_node` for details about returned dictionary.

	:rtype: dictionary or None
	"""	#pylint: disable=W0105

	root_name = property(_get_root_name, None, None, doc='Tree root node name')
	"""
	Gets the tree root node name, :code:`None` if the :py:class:`putil.tree.Tree` object has no nodes. See `NodeName`_ pseudo-type specification

	:rtype: NodeName or None
	"""	#pylint: disable=W0105
