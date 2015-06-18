# misc_example_3.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0702

from __future__ import print_function
import sys, putil.misc

def write_data(file_handle):
    if sys.version_info.major == 2:
        file_handle.write('Hello world!')
    else:
        file_handle.write(bytes('Hello world!', 'ascii'))

def show_tmpfile():
    with putil.misc.TmpFile(write_data) as fname:
        with open(fname, 'r') as fobj:
            lines = fobj.readlines()
    print('\n'.join(lines))
