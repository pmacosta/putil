# misc_example_3.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

from __future__ import print_function
import putil.misc

def write_data(file_handle):
    file_handle.write('Hello world!')

def show_tmpfile():
    with putil.misc.TmpFile(write_data) as fname:
        with open(fname, 'r') as fobj:
            lines = fobj.readlines()
    print('\n'.join(lines))
