.. tree.rst
.. Copyright (c) 2013-2015 Pablo Acosta-Serafini
.. See LICENSE for details
.. _tree-module:

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

*******
License
*******

The MIT License (MIT)

Copyright (c) 2013-2015 Pablo Acosta-Serafini

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
