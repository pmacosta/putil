# files.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

import sys

if sys.version_info.major == 2:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write


###
# Functions
###
def write_cols_not_unique(file_handle):
    _write(file_handle, 'Col1,Col2,Col3,Col1')


def write_data_start_file(file_handle):
    _write(file_handle, 'Ctrl,Ref,Result\n')
    _write(file_handle, '"a","+inf","real"\n')
    _write(file_handle, '"b","c","d"\n')
    _write(file_handle, '2,"",30\n')
    _write(file_handle, '2,5,40\n')
    _write(file_handle, '3,5,50\n')


def write_empty_cols(file_handle):
    _write(file_handle, 'Col1,Col2,Col3\n')
    _write(file_handle, '1,"",10\n')
    _write(file_handle, '1,4,\n')


def write_file(file_handle):
    _write(file_handle, 'Ctrl,Ref,Result\n')
    _write(file_handle, '1,3,10\n')
    _write(file_handle, '1,4,20\n')
    _write(file_handle, '2,4,30\n')
    _write(file_handle, '2,5,40\n')
    _write(file_handle, '3,5,50\n')


def write_file_empty(file_handle):
    _write(file_handle, '')


def write_input_file(file_handle):
    _write(file_handle, 'Ctrl,Ref,Data1,Data2\n')
    _write(file_handle, '"nom",10,20,30\n')
    _write(file_handle, '"high",20,40,60\n')
    _write(file_handle, '"low",30,300,3000\n')


def write_no_data(file_handle):
    _write(file_handle, 'Col1,Col2,Col3')


def write_no_header_file(file_handle):
    _write(file_handle, '1,4,7\n')
    _write(file_handle, '2,5,8\n')
    _write(file_handle, '3,6,9\n')
    _write(file_handle, '1,6,6\n')


def write_replacement_file(file_handle):
    _write(file_handle, 'H1,H2,H3,H4\n')
    _write(file_handle, '1,2,3,4\n')
    _write(file_handle, '5,6,7,8\n')
    _write(file_handle, '9,10,11,12\n')


def write_sort_file(file_handle):
    _write(file_handle, 'H1,H2,H3\n')
    _write(file_handle, '3,6,10\n')
    _write(file_handle, '3,2,20\n')
    _write(file_handle, '3,1,30\n')
    _write(file_handle, '1,2,10\n')
    _write(file_handle, '1,1,20\n')
    _write(file_handle, '1,2,5\n')
    _write(file_handle, '4,7,10\n')
    _write(file_handle, '4,5,20\n')
    _write(file_handle, '4,8,30\n')


def write_str_cols_file(file_handle):
    _write(file_handle, 'Ctrl,Ref\n')
    _write(file_handle, '"nom",10\n')
    _write(file_handle, '"high",20\n')
    _write(file_handle, '"low",30\n')
