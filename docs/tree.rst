.. tree.rst
.. Copyright (c) 2013-2016 Pablo Acosta-Serafini
.. See LICENSE for details
.. py:module:: putil.tree

###########
tree module
###########

This module can be used to build, handle, process and search
`tries <http://wikipedia.org/wiki/Trie>`_

*******
Classes
*******

.. autoclass:: putil.tree.Tree
    :members: add_nodes, collapse_subtree, copy_subtree, delete_prefix,
              delete_subtree, flatten_subtree, get_children, get_data,
              get_leafs, get_node, get_node_children, get_node_parent,
			  get_subtree, is_root, in_tree, is_leaf, make_root, print_node,
			  rename_node, search_tree, nodes, node_separator, root_node,
			  root_name, __nonzero__, __str__
    :show-inheritance:
