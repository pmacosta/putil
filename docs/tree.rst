.. _tree-module:

###########
tree module
###########



This module can be used to build, handle, process and search `tries <http://wikipedia.org/wiki/Trie>`_

***************************************
Application programming interface (API)
***************************************

Pseudo-types
============

NodeName
--------

A tree node name is a *string* where hierarchy levels are denoted by node separator characters (:code:`'.'` by default). Node names cannot contain spaces, empty hierarchy levels, start or end with a node separator character.

For this example tree::

	root
	├branch1
	│├leaf1
	│└leaf2
	└branch2

The node names are ``'root'``, ``'root.branch1'``, ``'root.branch1.leaf1'``, ``'root.branch1.leaf2'`` and ``'root.branch2'``.

NodesWithData
-------------

Dictionary or list of dictionaries. Each dictionary must contain exactly two keys:

* **name** (*NodeName*) Node name. See `NodeName`_ pseudo-type specification

* **data** (*any*) node data

The node data should be an empty list to create a node without data, for example: :code:`{'name':'a.b.c', 'data':list()}`

Classes
=======

.. automodule:: putil.tree
    :members: Tree
    :undoc-members:
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
