#!/usr/bin/env python
# build_moddb.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0914

# Standard library imports
import glob
import os
# Putil imports
import putil.pinspect


###
# Functions
###
def build_moddb():
    """
    Combine all individual traced modules information into as single
    traced modules information database
    """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(pkg_dir, 'docs')
    obj = putil.pinspect.Callables()
    db_file = os.path.join(docs_dir, 'moddb.json')
    for item in glob.glob(os.path.join(docs_dir, '*.json')):
        obj.load(item)
    obj.save(db_file)


if __name__ == '__main__':
    build_moddb()
