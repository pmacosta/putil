# tree_example.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import putil.tree

def create_tree():
    tobj = putil.tree.Tree()
    tobj.add_nodes([
        {'name':'root.branch1', 'data':5},
        {'name':'root.branch1', 'data':7},
        {'name':'root.branch2', 'data':[]},
        {'name':'root.branch1.leaf1', 'data':[]},
        {'name':'root.branch1.leaf1.subleaf1', 'data':333},
        {'name':'root.branch1.leaf2', 'data':'Hello world!'},
        {'name':'root.branch1.leaf2.subleaf2', 'data':[]},
    ])
    return tobj
