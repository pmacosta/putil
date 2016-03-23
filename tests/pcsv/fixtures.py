# fixtures.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# Standard library imports
from itertools import product
import sys
# Putil imports
import putil.misc
from putil.test import AE, AI, RE
if sys.hexversion < 0x03000000:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write


###
# Functions
###
def common_exceptions(obj):
    # pylint: disable=R0913,R0914
    # Input file exceptions
    file_items = [5, 'some_file\0']
    dfilter_items = [
        True,
        ['a', True],
        (['Ctrl'], 'a'),
        (['Ctrl'], {}),
        ({5:True}, ['Ctrl']),
        ({'a':{'xx':2}}, ['Ctrl']),
        (['Ctrl'], {'a':[3, {'xx':2}]})
    ]
    for file_toggle in [False, True]:
        # File-related tests
        with putil.misc.TmpFile(write_file) as real_file:
            fname1 = '_dummy_file_' if not file_toggle else real_file
            fname2 = real_file if not file_toggle else '_dummy_file_'
            exmsg = 'File _dummy_file_ could not be found'
            AE(obj, OSError, exmsg, fname1, fname2, ['a'], ['b'])
            for item in file_items:
                fname1 = item if not file_toggle else real_file
                fname2 = real_file if not file_toggle else item
                par = 'fname1' if not file_toggle else 'fname2'
                AI(obj, par, fname1, fname2, ['a'], ['b'])
        dfilter = ['Ctrl']
        with putil.misc.TmpFile(write_file_empty) as empty_file:
            with putil.misc.TmpFile(write_file) as real_file:
                fname1 = empty_file if not file_toggle else real_file
                fname2 = real_file if not file_toggle else empty_file
                exmsg = r'File (.+) is empty'
                AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter)
        with putil.misc.TmpFile(write_cols_not_unique) as nuniq_file:
            with putil.misc.TmpFile(write_file) as real_file:
                fname1 = nuniq_file if not file_toggle else real_file
                fname2 = real_file if not file_toggle else nuniq_file
                exmsg = 'Column headers are not unique in file (.+)'
                AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter)
        # Filter-related exceptions
        with putil.misc.TmpFile(write_file) as fname1:
            with putil.misc.TmpFile(write_file) as fname2:
                for item in dfilter_items:
                    dfilter1 = item if not file_toggle else ['Ctrl']
                    dfilter2 = ['Ctrl'] if not file_toggle else item
                    par = 'dfilter1' if not file_toggle else 'dfilter2'
                    AI(obj, par, fname1, fname2, dfilter1, dfilter2)
                item = (['Ctrl'], {'aaa':5})
                dfilter1 = item if not file_toggle else ['Ctrl']
                dfilter2 = ['Ctrl'] if not file_toggle else item
                exmsg = 'Column aaa not found'
                AE(obj, ValueError, exmsg, fname1, fname2, dfilter1, dfilter2)
                # Columns-related exceptions
                dfilter1 = ['NoCol'] if not file_toggle else ['Ref']
                dfilter2 = ['Ref'] if not file_toggle else ['NoCol']
                exmsg = 'Column NoCol not found'
                AE(obj, ValueError, exmsg, fname1, fname2, dfilter1, dfilter2)
                dfilter1 = ['0'] if not file_toggle else ['Ref']
                dfilter2 = ['Ref'] if not file_toggle else ['0']
                exmsg = 'Invalid column specification'
                AE(
                    obj, RE, exmsg,
                    fname1, fname2,
                    dfilter1, dfilter2,
                    file_toggle, not file_toggle
                )
    # Starting row
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            # Invalid row_start
            for item, par in product(['a', True, -1], ['frow1', 'frow2']):
                AI(obj, par, fname1, fname2, dfilter, dfilter, **{par:item})
            exmsg = 'File {0} has no valid data'.format(fname1)
            AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter, frow1=200)
            exmsg = 'File {0} has no valid data'.format(fname2)
            AE(obj, RE, exmsg, fname1, fname2, dfilter, dfilter, frow2=200)
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as fname1:
        with putil.misc.TmpFile(write_file) as fname2:
            par = 'ofname'
            for item in [7, 'a_file\0']:
                AI(obj, par, fname1, fname2, dfilter, ['Ref'], ofname=item)
            fname = 'some_file.csv'
            for item in [7, ['a', 'b', 5]]:
                AI(
                    obj, 'ocols', fname1, fname2, dfilter, ['Ref'],
                    ofname=fname, ocols=item
                )


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
