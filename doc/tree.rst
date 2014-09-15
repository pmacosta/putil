###########
tree module
###########



This module can be used to build, handle, process and search `tries <http://wikipedia.org/wiki/Trie>`_

***********
Interpreter
***********

The module has been developed using Python 2.7, but it *should* also work with Python 3.x

******************
External libraries
******************

Standard Python library and other Putil library modules

***************************************
Application programming interface (API)
***************************************
Pseudo-types
============

NodeName
--------

The tree node name is a *string* where hierarchy levels are denoted by a period '.' in the name. Node names cannot contain spaces, empty hierarchy levels, start with a period or end with a period.

For this example tree::

	root
	├branch1
	│├leaf1
	│└leaf2
	└branch2

The node names are ``'root'``, ``'root.branch1'``, ``'root.branch1.leaf1'``, ``'root.branch1.leaf2'`` and ``'root.branch2'``.

Global variables
================

None

Functions
=========

None

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

Copyright (c) 2013-2014 Pablo Acosta-Serafini

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
