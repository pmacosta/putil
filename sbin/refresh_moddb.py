#!/usr/bin/env python
# refresh_moddb.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os
# Putil imports
import putil.pinspect


###
# Functions
###
def refresh_moddb():
    """
    Refresh traced modules information database
    """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(pkg_dir, 'docs')
    db_file = os.path.join(docs_dir, 'moddb.json')
    if os.path.exists(db_file):
        obj = putil.pinspect.Callables()
        obj.load(db_file)
        obj.refresh()
        obj.save(db_file)


if __name__ == '__main__':
    refresh_moddb()
