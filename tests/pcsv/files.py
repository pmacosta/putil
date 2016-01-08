# files.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# Standard library imports
import sys
# Putil imports
if sys.hexversion < 0x03000000:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write


###
# Functions
###
def write_array(file_handle, lines):
    lines = lines if isinstance(lines, list) else [lines]
    for line in lines:
        _write(file_handle, line+('\n' if line else ''))


def write_cols_not_unique(file_handle):
    write_array(file_handle, 'Col1,Col2,Col3,Col1')


def write_data_start_file(file_handle):
    lines = [
        'Ctrl,Ref,Result',
        '"a","+inf","real"',
        '"b","c","d"',
        '2,"",30',
        '2,5,40',
        '3,5,50',
    ]
    write_array(file_handle, lines)


def write_empty_cols(file_handle):
    lines = [
        'Col1,Col2,Col3',
        '1,"",10',
        '1,4,',
    ]
    write_array(file_handle, lines)


def write_file(file_handle):
    lines = [
        'Ctrl,Ref,Result',
        '1,3,10',
        '1,4,20',
        '2,4,30',
        '2,5,40',
        '3,5,50',
    ]
    write_array(file_handle, lines)


def write_file_empty(file_handle):
    write_array(file_handle, '')


def write_input_file(file_handle):
    lines = [
        'Ctrl,Ref,Data1,Data2',
        '"nom",10,20,30',
        '"high",20,40,60',
        '"low",30,300,3000',
    ]
    write_array(file_handle, lines)


def write_no_data(file_handle):
    write_array(file_handle, 'Col1,Col2,Col3')


def write_no_header_file(file_handle):
    lines = [
        '1,4,7',
        '2,5,8',
        '3,6,9',
        '1,6,6',
    ]
    write_array(file_handle, lines)


def write_replacement_file(file_handle):
    lines = [
        'H1,H2,H3,H4',
        '1,2,3,4',
        '5,6,7,8',
        '9,10,11,12',
    ]
    write_array(file_handle, lines)


def write_sort_file(file_handle):
    lines = [
        'H1,H2,H3',
        '3,6,10',
        '3,2,20',
        '3,1,30',
        '1,2,10',
        '1,1,20',
        '1,2,5',
        '4,7,10',
        '4,5,20',
        '4,8,30',
    ]
    write_array(file_handle, lines)


def write_str_cols_file(file_handle):
    lines = [
        'Ctrl,Ref',
        '"nom",10',
        '"high",20',
        '"low",30',
    ]
    write_array(file_handle, lines)
