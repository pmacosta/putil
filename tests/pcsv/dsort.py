# dsort.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

# PyPI imports
import pytest
# Putil imports
import putil.misc
import putil.pcsv
import putil.test
from putil.test import AE, AI, RE
from tests.pcsv.fixtures import (
    write_cols_not_unique,
    write_file,
    write_file_empty
)


###
# Test functions
###
def test_dsort_function():
    """ Test dsort function behavior """
    # Input file name has headers, separate output file name
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_file) as fname:
            putil.pcsv.dsort(
                fname, [{'Ctrl':'D'}, {'Ref':'A'}], True, ofname=ofname
            )
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
    assert obj.header() == ['Ctrl', 'Ref', 'Result']
    assert obj.data() == [
        [3, 5, 50], [2, 4, 30], [2, 5, 40], [1, 3, 10], [1, 4, 20]
    ]
    # Input file name does not have headers, separate output file name
    with putil.misc.TmpFile() as ofname:
        with putil.misc.TmpFile(write_file) as fname:
            putil.pcsv.dsort(fname, [{0:'D'}, {1:'A'}], False, ofname=ofname)
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=False)
    assert obj.header() == [0, 1, 2]
    assert obj.data() == [
        [3, 5, 50], [2, 4, 30], [2, 5, 40], [1, 3, 10], [1, 4, 20]
    ]
    # "In place" sort
    with putil.misc.TmpFile(write_file) as fname:
        putil.pcsv.dsort(fname, [{0:'D'}, {1:'A'}], False)
        obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
    assert obj.header() == [0, 1, 2]
    assert obj.data() == [
        [3, 5, 50], [2, 4, 30], [2, 5, 40], [1, 3, 10], [1, 4, 20]
    ]
    # Starting row
    with putil.misc.TmpFile(write_file) as fname:
        putil.pcsv.dsort(fname, [{0:'D'}, {1:'A'}], False, 4)
        obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
    assert obj.header() == [0, 1, 2]
    assert obj.data() == [[3, 5, 50], [2, 4, 30], [2, 5, 40]]


@pytest.mark.dsort
def test_dsort_function_exceptions():
    """ Test dsort function exceptions """
    obj = putil.pcsv.dsort
    # Input file exceptions
    exmsg = 'File _dummy_file_ could not be found'
    AE(obj, OSError, exmsg, fname='_dummy_file_', order=['a'])
    for item in [5, 'some_file\0']:
        AI(obj, '*[fname]*', fname=item, order=['a'])
    with putil.misc.TmpFile(write_file) as fname:
        AI(obj, 'order', fname=fname, order=True)
    with putil.misc.TmpFile(write_file_empty) as fname:
        AE(obj, RE, r'File (.+) is empty', fname=fname, order=['a'])
    with putil.misc.TmpFile(write_cols_not_unique) as fname:
        exmsg = 'Column headers are not unique in file (.+)'
        AE(obj, RE, exmsg, fname=fname, order=['Col1'])
    with putil.misc.TmpFile(write_file) as fname:
        AE(obj, ValueError, 'Column aaa not found', fname=fname, order=['aaa'])
    with putil.misc.TmpFile(write_file) as fname:
        exmsg = 'Invalid column specification'
        AE(obj, RE, exmsg, fname=fname, has_header=False, order=['0'])
    with putil.misc.TmpFile(write_file) as fname:
        AI(obj, 'has_header', fname=fname, order=['Ctrl'], has_header=5)
    with putil.misc.TmpFile(write_file) as fname:
        for item in ['a', True, -1]:
            AI(obj, 'frow', fname=fname, order=['A'], frow=item)
        exmsg = 'File {0} has no valid data'.format(fname)
        AE(obj, RE, exmsg, fname=fname, order=['A'], frow=10)
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as fname:
        for item in [7, 'a_file\0']:
            AI(obj, 'ofname', fname=fname, order=['Ctrl'], ofname=item)
