# dsort.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0915,W0232

import pytest
import tempfile

import putil.pcsv
import putil.test
from tests.pcsv.files import (
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
    with tempfile.NamedTemporaryFile() as fwobj:
        ofname = fwobj.name
        with putil.misc.TmpFile(write_file) as fname:
            putil.pcsv.dsort(
                fname=fname,
                order=[{'Ctrl':'D'}, {'Ref':'A'}],
                has_header=True,
                ofname=ofname
            )
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=True)
    assert obj.header() == ['Ctrl', 'Ref', 'Result']
    assert (
        obj.data()
        ==
        [
            [3, 5, 50],
            [2, 4, 30],
            [2, 5, 40],
            [1, 3, 10],
            [1, 4, 20]
        ]
    )
    # Input file name does not have headers, separate output file name
    with tempfile.NamedTemporaryFile() as fwobj:
        ofname = fwobj.name
        with putil.misc.TmpFile(write_file) as fname:
            putil.pcsv.dsort(
                fname=fname,
                order=[{0:'D'}, {1:'A'}],
                has_header=False,
                ofname=ofname
            )
        obj = putil.pcsv.CsvFile(fname=ofname, has_header=False)
    assert obj.header() == [0, 1, 2]
    assert (
        obj.data()
        ==
        [
            [3, 5, 50],
            [2, 4, 30],
            [2, 5, 40],
            [1, 3, 10],
            [1, 4, 20]
        ]
    )
    # "In place" sort
    with putil.misc.TmpFile(write_file) as fname:
        putil.pcsv.dsort(
            fname=fname,
            order=[{0:'D'}, {1:'A'}],
            has_header=False
        )
        obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
    assert obj.header() == [0, 1, 2]
    assert (
        obj.data()
        ==
        [
            [3, 5, 50],
            [2, 4, 30],
            [2, 5, 40],
            [1, 3, 10],
            [1, 4, 20]
        ]
    )


@pytest.mark.dsort
def test_dsort_function_exceptions():
    """ Test dsort function exceptions """
    # Input file exceptions
    putil.test.assert_exception(
        putil.pcsv.dsort,
        {
            'fname':'_dummy_file_',
            'order':['a'],
        },
        OSError,
        'File _dummy_file_ could not be found'
    )
    putil.test.assert_exception(
        putil.pcsv.dsort,
        {
            'fname':5,
            'order':['a'],
        },
        RuntimeError,
        'Argument `*[fname]*` is not valid'
    )
    putil.test.assert_exception(
        putil.pcsv.dsort,
        {
            'fname':'some_file\0',
            'order':['a'],
        },
        RuntimeError,
        'Argument `*[fname]*` is not valid'
    )
    with putil.misc.TmpFile(write_file) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':True,
            },
            RuntimeError,
            'Argument `order` is not valid'
        )
    with putil.misc.TmpFile(write_file_empty) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['a'],
            },
            RuntimeError,
            r'File (.+) is empty'
        )
    with putil.misc.TmpFile(write_cols_not_unique) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['Col1'],
            },
            RuntimeError,
            'Column headers are not unique in file (.+)'
        )
    with putil.misc.TmpFile(write_file) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['aaa'],
            },
            ValueError,
            'Column aaa not found'
        )
    with putil.misc.TmpFile(write_file) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'has_header':False,
                'order':['0'],
            },
            RuntimeError,
            'Invalid column specification'
        )
    with putil.misc.TmpFile(write_file) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['Ctrl'],
                'has_header':5,
            },
            RuntimeError,
            'Argument `has_header` is not valid'
        )
    # Output file exceptions
    with putil.misc.TmpFile(write_file) as fname:
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['Ctrl'],
                'ofname':7
            },
            RuntimeError,
            'Argument `ofname` is not valid'
        )
        putil.test.assert_exception(
            putil.pcsv.dsort,
            {
                'fname':fname,
                'order':['Ctrl'],
                'ofname':'a_file\0'
            },
            RuntimeError,
            'Argument `ofname` is not valid'
        )
