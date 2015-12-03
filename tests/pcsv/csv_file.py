# csv_file.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0302,E0611,F0401,R0201,R0204,R0915,W0232

# Standard library imports
import os
import sys
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import pytest
if sys.hexversion < 0x03000000:
    import mock
# Putil imports
import putil.misc
import putil.pcsv
import putil.test
if sys.hexversion < 0x03000000:
    from putil.compat2 import _read
else:
    from putil.compat3 import _read
from tests.pcsv.files import (
    write_cols_not_unique,
    write_data_start_file,
    write_empty_cols,
    write_file,
    write_file_empty,
    write_no_data,
    write_no_header_file,
    write_sort_file,
    write_str_cols_file
)


###
# Test classes
###
class TestCsvFile(object):
    """ Tests for CsvFile class """
    # pylint: disable=R0904
    @pytest.mark.csv_file
    def test_init_exceptions(self):
        """ Test constructor exceptions """
        fname = os.path.join(
            os.path.abspath(os.sep),
            'file',
            'does',
            'not',
            'exists.csv'
        )
        func_pointers = [
            (RuntimeError, 'File {0} is empty', write_file_empty),
            (
                RuntimeError,
                'Column headers are not unique in file {0}',
                write_cols_not_unique
            ),
            (RuntimeError, 'File {0} has no valid data', write_no_data)
        ]
        putil.test.assert_exception(
            putil.pcsv.CsvFile,
            {'fname':5},
            RuntimeError,
            'Argument `fname` is not valid'
        )
        putil.test.assert_exception(
            putil.pcsv.CsvFile,
            {'fname':fname},
            OSError,
            'File {0} could not be found'.format(fname)
        )
        for extype, exmsg, fobj in func_pointers:
            with pytest.raises(extype) as excinfo:
                with putil.misc.TmpFile(fobj) as fname:
                    putil.pcsv.CsvFile(fname=os.path.normpath(fname))
            ref = (exmsg.format(fname) if '{0}' in exmsg else exmsg)
            assert putil.test.get_exmsg(excinfo) == os.path.normpath(ref)
        with putil.misc.TmpFile(write_file) as fname:
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'has_header':5},
                RuntimeError,
                'Argument `has_header` is not valid'
            )
        with putil.misc.TmpFile(write_file) as fname:
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':5.2},
                RuntimeError,
                'Argument `dfilter` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':5, 'has_header':True},
                ValueError,
                'Column 5 not found'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':5, 'has_header':False},
                ValueError,
                'Column 5 not found'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':'A', 'has_header':False},
                RuntimeError,
                'Invalid column specification'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':'aa'},
                ValueError,
                'Column aa not found'
            )

    def test_eq(self):
        """ Test __eq__ method behavior """
        # pylint: disable=C0113
        with putil.misc.TmpFile() as fname:
            putil.pcsv.write(fname, [['a'], [1]], append=False)
            obj1 = putil.pcsv.CsvFile(fname, dfilter='a')
            obj2 = putil.pcsv.CsvFile(fname, dfilter='a')
        with putil.misc.TmpFile() as fname:
            putil.pcsv.write(fname, [['a'], [2]], append=False)
            obj3 = putil.pcsv.CsvFile(fname, dfilter='a')
        assert obj1 == obj2
        assert obj1 != obj3
        assert not obj3 == 5

    def test_repr(self):
        """ Test __repr__ method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert (
            repr(obj)
            ==
            "putil.pcsv.CsvFile(fname=r'{0}')".format(os.path.normpath(fname))
        )
        obj.dfilter = 'Ctrl'
        assert (
            repr(obj)
            ==
            "putil.pcsv.CsvFile(fname=r'{0}', dfilter=['Ctrl'])".format(
                os.path.normpath(fname)
            )
        )
        obj.dfilter = {'Ctrl':2}
        assert (
            repr(obj)
            ==
            (
                "putil.pcsv.CsvFile(fname=r'{0}', "
                "dfilter={{'Ctrl': 2}})".format(os.path.normpath(fname))
            )
        )
        obj.dfilter = ('Ctrl', {'Result': 40})
        assert (
            repr(obj)
            ==
            (
                "putil.pcsv.CsvFile(fname=r'{0}', "
                "dfilter=({{'Result': 40}}, ['Ctrl']))".format(
                    os.path.normpath(fname)
                )
            )
        )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        assert (
            repr(obj)
            ==
            "putil.pcsv.CsvFile(fname=r'{0}', has_header=False)".format(
                os.path.normpath(fname)
            )
        )
        obj.dfilter = 0
        assert (
            repr(obj)
            ==
            (
                "putil.pcsv.CsvFile(fname=r'{0}', "
                "dfilter=[0], has_header=False)".format(
                    os.path.normpath(fname)
                )
            )
        )
        obj.dfilter = {0:2}
        assert (
            repr(obj)
            ==
            (
                "putil.pcsv.CsvFile(fname=r'{0}', "
                "dfilter={{0: 2}}, has_header=False)".format(
                    os.path.normpath(fname)
                )
            )
        )
        obj.dfilter = (0, {2: 40})
        assert (
            repr(obj)
            ==
            (
                "putil.pcsv.CsvFile(fname=r'{0}', "
                "dfilter=({{2: 40}}, [0]), "
                "has_header=False)".format(os.path.normpath(fname))
            )
        )

    def test_str(self):
        """ Test __str__ method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=os.path.normpath(fname))
        ref = (
            'File: {0}\n'
            "Header: ['Ctrl', 'Ref', 'Result']\n"
            'Row filter: None\n'
            'Column filter: None\n'
            'Rows: 5\n'
            'Columns: 3'.format(os.path.normpath(fname))
        )
        assert str(obj) == ref
        obj.cfilter = 'Ref'
        ref = (
            'File: {0}\n'
            "Header: ['Ctrl', 'Ref', 'Result']\n"
            'Row filter: None\n'
            "Column filter: ['Ref']\n"
            'Rows: 5\n'
            'Columns: 3 (1 filtered)'.format(os.path.normpath(fname))
        )
        assert str(obj) == ref
        obj.rfilter = {'Ctrl':[1, 3]}
        ref = (
            'File: {0}\n'
            "Header: ['Ctrl', 'Ref', 'Result']\n"
            "Row filter: {{'Ctrl': [1, 3]}}\n"
            "Column filter: ['Ref']\n"
            'Rows: 5 (3 filtered)\n'
            'Columns: 3 (1 filtered)'.format(os.path.normpath(fname))
        )
        assert str(obj) == ref

    def test_data_start(self):
        """ Test if the right row is picked for the data start """
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.data() == [[2, None, 30], [2, 5, 40], [3, 5, 50]]
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        assert obj.data() == [[1, 4, 7], [2, 5, 8], [3, 6, 9], [1, 6, 6]]
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, frow=5)
        assert obj.data() == [[2, 5, 40], [3, 5, 50]]
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False, frow=2)
        assert obj.data() == [[2, 5, 8], [3, 6, 9], [1, 6, 6]]

    def test_data_start_exceptions(self):
        """ Test frow parameter exceptions """
        with putil.misc.TmpFile(write_data_start_file) as fname:
            for item in ['a', True, -1]:
                putil.test.assert_exception(
                    putil.pcsv.CsvFile,
                    {'fname':fname, 'frow':item},
                    RuntimeError,
                    'Argument `frow` is not valid'
                )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'frow':10},
                RuntimeError,
                'File {0} has no valid data'.format(fname)
            )

    def test_add_dfilter(self):
        """ Test add_dfilter method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            obj.add_dfilter(None)
            ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
            assert obj.data(filtered=True) == ref
            obj.add_dfilter({'Ctrl':1})
            obj.add_dfilter({'Result':20})
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.add_dfilter(1)
            assert obj.data(filtered=True) == [[4]]
            obj.reset_dfilter()
            assert obj.data(filtered=True) == ref
            obj.add_dfilter(({'Result':20}, 1))
            assert obj.data(filtered=True) == [[4]]
            # Two single elements
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.add_dfilter({'Result':40})
            assert obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40]]
            # Single element to list
            obj.reset_dfilter('R')
            obj.dfilter = {'Result':[10, 30]}
            assert obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30]]
            obj.add_dfilter({'Result':50})
            assert (
                obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30], [3, 5, 50]]
            )
            obj.add_dfilter(([0, 2], {'Result':50}))
            assert (obj.data(filtered=True) == [[1, 10], [2, 30], [3, 50]])
            # List to list
            obj.reset_dfilter(True)
            obj.dfilter = {'Result':[10, 20]}
            assert obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20]]
            obj.add_dfilter({'Result':[40, 50]})
            ref = [[1, 3, 10], [1, 4, 20], [2, 5, 40], [3, 5, 50]]
            assert obj.data(filtered=True) == ref
            obj.add_dfilter(2)
            assert obj.data(filtered=True) == [[10], [20], [40], [50]]
            obj.add_dfilter(['Ctrl'])
            ref = [[10, 1], [20, 1], [40, 2], [50, 3]]
            assert obj.data(filtered=True) == ref
            # List to single element
            obj.reset_dfilter()
            obj.dfilter = {'Result':20}
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.add_dfilter({'Result':[40, 50]})
            assert (
                obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40], [3, 5, 50]]
            )
            # Columns specified as numbers
            obj.reset_dfilter()
            obj.dfilter = {2:20}
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.dfilter = {0:1, 2:10}
            assert obj.data(filtered=True) == [[1, 3, 10]]
            # Swap columns by specifying different order in column filter
            obj.dfilter = ['Result', 'Ref', 'Ctrl']
            assert (
                obj.data(filtered=True)
                ==
                [[10, 3, 1], [20, 4, 1], [30, 4, 2], [40, 5, 2], [50, 5, 3]]
            )
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter={0:3}, has_header=False
            )
            obj.add_dfilter({0:1})
            assert obj.data(filtered=True) == [[1, 4, 7], [3, 6, 9], [1, 6, 6]]

    @pytest.mark.csv_file
    def test_add_dfilter_exceptions(self):
        """ Test add_dfilter method exceptions """
        items = [
            True,
            (1, 2, 3),
            (True, 'A'),
            (True, ),
            (None, True),
            ('A', 'A'),
            ({'B':1}, {'C':5}),
            {2.0:5},
            ({2.0:5}, 'A'),
            (['A', True], {'A':1}),
            ('A', {}),
            ([], {'A':1}),
            ({}, []),
            {'dfilter':{'a':{'xx':2}}},
            {'dfilter':{'a':[3, {'xx':2}]}}
        ]
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            for item in items:
                putil.test.assert_exception(
                    obj.add_dfilter,
                    {'dfilter':item},
                    RuntimeError,
                    'Argument `dfilter` is not valid'
                )
            putil.test.assert_exception(
                obj.add_dfilter,
                {'dfilter':{'aaa':5}},
                ValueError,
                'Column aaa not found'
            )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
            putil.test.assert_exception(
                obj.add_dfilter,
                {'dfilter':{10:5}},
                ValueError,
                'Column 10 not found'
            )
            putil.test.assert_exception(
                obj.add_dfilter,
                {'dfilter':'25'},
                RuntimeError,
                'Invalid column specification'
            )

    def test_cols(self):
        """ Test cols method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter=[0, 2])
        assert obj.cols() == 3
        assert obj.cols(filtered=True) == 2

    @pytest.mark.csv_file
    def test_cols_exceptions(self):
        """ Test cols method exceptions """
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        items = [1, 'x']
        for item in items:
            putil.test.assert_exception(
                obj.cols,
                {'filtered':item},
                RuntimeError,
                'Argument `filtered` is not valid'
            )

    def test_data(self):
        """ Test data method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
        assert obj.data() == ref
        assert obj.data(filtered=True) == [[1, 4, 20]]
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter=({'Result':20}, 'Ref')
            )
        assert obj.data(filtered='C') == [[3], [4], [4], [5], [5]]
        assert obj.data(filtered='b') == [[4]]
        ref = [[1, 10], [1, 20], [2, 30], [2, 40], [3, 50]]
        obj.cfilter = ['Ctrl', 'Result']
        assert obj.data(filtered='c') == ref
        assert obj.data(filtered=True) == [[1, 20]]
        obj.cfilter = [0, 2]
        assert obj.data(filtered='B') == [[1, 20]]
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter=[0, 2], has_header=False
            )
        assert obj.data(filtered='C') == [[1, 7], [2, 8], [3, 9], [1, 6]]

    @pytest.mark.csv_file
    def test_data_exceptions(self):
        """ Test data method exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        putil.test.assert_exception(
            obj.data,
            {'filtered':5},
            RuntimeError,
            'Argument `filtered` is not valid'
        )
        obj.data()
        obj.data(filtered=True)
        obj.add_dfilter('Ctrl')
        assert obj.cfilter == ['Ctrl']
        assert obj.rfilter == {'Result':20}
        obj.data()
        assert obj.dfilter == ({'Result':20}, ['Ctrl'])
        obj.data()

    def test_dsort(self):
        """ Test dsort method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        obj.dsort([{'Ctrl':'D'}, {'Ref':'A'}])
        assert (
            obj.data()
            ==
            [
                [3, 5, 50],
                [2, 4, 30],
                [2, 5, 40],
                [1, 3, 10],
                [1, 4, 20],
            ]
        )
        obj.dsort([{'Ctrl':'D'}, {'Ref':'D'}])
        assert (
            obj.data()
            ==
            [
                [3, 5, 50],
                [2, 5, 40],
                [2, 4, 30],
                [1, 4, 20],
                [1, 3, 10],
            ]
        )
        obj.dsort(['Ctrl', 'Ref'])
        assert (
            obj.data()
            ==
            [
                [1, 3, 10],
                [1, 4, 20],
                [2, 4, 30],
                [2, 5, 40],
                [3, 5, 50],
            ]
        )
        with putil.misc.TmpFile(write_sort_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        obj.dsort([{'H1':'A'}, {'H2':'A'}, {'H3':'A'}])
        assert (
            obj.data()
            ==
            [
                [1, 1, 20],
                [1, 2, 5],
                [1, 2, 10],
                [3, 1, 30],
                [3, 2, 20],
                [3, 6, 10],
                [4, 5, 20],
                [4, 7, 10],
                [4, 8, 30],
            ]
        )
        obj.dsort([{'H1':'D'}, {'H2':'A'}, {'H3':'D'}])
        assert (
            obj.data()
            ==
            [
                [4, 5, 20],
                [4, 7, 10],
                [4, 8, 30],
                [3, 1, 30],
                [3, 2, 20],
                [3, 6, 10],
                [1, 1, 20],
                [1, 2, 10],
                [1, 2, 5],
            ]
        )

    @pytest.mark.csv_file
    def test_dsort_exceptions(self):
        """ Test dsort method exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        for item in [None, []]:
            putil.test.assert_exception(
                obj.dsort,
                {'order':item},
                RuntimeError,
                'Argument `order` is not valid'
            )
        putil.test.assert_exception(
            obj.dsort,
            {'order':'a'},
            ValueError,
            'Column a not found'
        )
        putil.test.assert_exception(
            obj.dsort,
            {'order':['Ctrl', 'a']},
            ValueError,
            'Column a not found'
        )
        putil.test.assert_exception(
            obj.dsort,
            {'order':['Ctrl', {'a':'d'}]},
            ValueError,
            'Column a not found'
        )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        putil.test.assert_exception(
            obj.dsort,
            {'order':'0'},
            RuntimeError,
            'Invalid column specification'
        )

    def test_header(self):
        """ Test header method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.header() == ['Ctrl', 'Ref', 'Result']
        assert obj.header(True) == ['Ctrl', 'Ref', 'Result']
        obj.dfilter = ['Result', 'Ctrl']
        assert obj.header() == ['Ctrl', 'Ref', 'Result']
        assert obj.header(True) == ['Result', 'Ctrl']
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        assert obj.header() == [0, 1, 2]
        assert obj.header(True) == [0, 1, 2]
        obj.cfilter = [2, 1]
        assert obj.header() == [0, 1, 2]
        assert obj.header(True) == [2, 1]

    @pytest.mark.csv_file
    def test_header_exceptions(self):
        """ Test header method exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        putil.test.assert_exception(
            obj.header,
            {'filtered':5},
            RuntimeError,
            'Argument `filtered` is not valid'
        )

    def test_replace(self):
        """ Test replace method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        obj.cfilter = ['Ref']
        obj.replace([[1.0], [2.0], [3.0], [4.5], [5.0]], filtered='C')
        assert (
            obj.data()
            ==
            [
                [1, 1.0, 10],
                [1, 2.0, 20],
                [2, 3.0, 30],
                [2, 4.5, 40],
                [3, 5.0, 50],
            ]
        )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        obj.cfilter = [0, 2]
        obj.replace(
            [[1.0, 'a'], [2.0, 'b'], [3.0, 'c'], [4.5, 'd'], [5.0, 'e']],
            True
        )
        assert (
            obj.data()
            ==
            [
                [1.0, 3, 'a'],
                [2.0, 4, 'b'],
                [3.0, 4, 'c'],
                [4.5, 5, 'd'],
                [5.0, 5, 'e'],
            ]
        )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname,
                dfilter=({'Ctrl':2}, [0, 2])
            )
        obj.replace(
            [[1.0, 'a'], [2.0, 'b']],
            filtered=True
        )
        assert (
            obj.data()
            ==
            [
                [1, 3, 10],
                [1, 4, 20],
                [1.0, 4, 'a'],
                [2.0, 5, 'b'],
                [3, 5, 50],
            ]
        )
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, has_header=False
            )
        obj.dfilter = [1]
        obj.replace([['a'], ['b'], ['c'], ['d']], True)
        assert (
            obj.data()
            ==
            [
                [1, 'a', 7],
                [2, 'b', 8],
                [3, 'c', 9],
                [1, 'd', 6],
            ]
        )
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter={0:1}, has_header=False
            )
        obj.cfilter = [0, 2]
        obj.replace(
            [[1.0, 'a'], [2.0, 'b']],
            filtered=True
        )
        assert (
            obj.data()
            ==
            [
                [1.0, 4, 'a'],
                [2, 5, 8],
                [3, 6, 9],
                [2.0, 6, 'b'],
            ]
        )

    @pytest.mark.csv_file
    def test_replace_exceptions(self):
        """ Test replace method exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            for item in [2.0, [2.0]]:
                putil.test.assert_exception(
                    obj.replace,
                    {'rdata':item},
                    RuntimeError,
                    'Argument `rdata` is not valid'
                )
            putil.test.assert_exception(
                obj.replace,
                {'rdata':[[2.0]], 'filtered':2.0},
                RuntimeError,
                'Argument `filtered` is not valid'
            )
            obj.cfilter = ['Ctrl']
            putil.test.assert_exception(
                obj.replace,
                {
                    'rdata':[[1]],
                    'filtered':False
                },
                ValueError,
               (
                   'Number of rows mismatch between '
                    'input and replacement data'
                )
            )
            obj.cfilter = ['Ctrl', 'Ref']
            putil.test.assert_exception(
                obj.replace,
                {
                    'rdata':[[1], [2], [3], [4], [5]],
                    'filtered':False
                },
                ValueError,
               (
                   'Number of columns mismatch between '
                    'input and replacement data'
                )
            )

    def test_reset_dfilter(self):
        """ Test reset_dfilter method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.dfilter == (None, None)
        ref = ('Ref', {'Ctrl':5})
        obj.dfilter = ref
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter()
        assert obj.dfilter == (None, None)
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter=({'Ctrl':5}, ['Ref'])
            )
        # No reset
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('N')
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('n')
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter(False)
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        # Column reset
        obj.reset_dfilter('C')
        assert obj.dfilter == ({'Ctrl':5}, None)
        obj.add_dfilter('Ref')
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('c')
        assert obj.dfilter == ({'Ctrl':5}, None)
        # Row reset
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('R')
        assert obj.dfilter == (None, ['Ref'])
        obj.add_dfilter({'Ctrl':5})
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('r')
        assert obj.dfilter == (None, ['Ref'])
        # Row and reset
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter()
        assert obj.dfilter == (None, None)
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter(True)
        assert obj.dfilter == (None, None)
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('B')
        assert obj.dfilter == (None, None)
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])
        obj.reset_dfilter('b')
        assert obj.dfilter == (None, None)
        obj.dfilter = ({'Ctrl':5}, ['Ref'])
        assert obj.dfilter == ({'Ctrl':5}, ['Ref'])

    @pytest.mark.csv_file
    def test_reset_dfilter_exceptions(self):
        """ Test reset_dfilter method exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        items = [
            2.0,
            'x',
            'BR'
        ]
        for item in items:
            putil.test.assert_exception(
                obj.reset_dfilter,
                {'ftype':item},
                RuntimeError,
                'Argument `ftype` is not valid'
            )

    def test_rows(self):
        """ Test rows method behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        assert obj.rows() == 5
        assert obj.rows(filtered=True) == 1

    @pytest.mark.csv_file
    def test_rows_exceptions(self):
        """ Test rows method exceptions """
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        putil.test.assert_exception(
            obj.rows,
            {'filtered':1},
            RuntimeError,
            'Argument `filtered` is not valid'
        )

    def test_write(self):
        """ Test write method behavior """
        lsep = '\r\n'
        # Check saving filtered data
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':1})
        ofname = fname
        with putil.misc.TmpFile() as fname:
            obj.cfilter = 'Result'
            obj.write(fname=fname, filtered=True, append=False)
            written_data = _read(fname)
        assert written_data == 'Result{0}10{0}20{0}'.format(lsep)
        # Test default fname with renamed single column
        obj.rfilter = {'Ctrl':2}
        obj.write(filtered=True, append=False, header='MyCol')
        written_data = _read(ofname)
        assert written_data == 'MyCol{0}30{0}40{0}'.format(lsep)
        obj.reset_dfilter()
        # Test repeated columns
        obj.rfilter = {'Ctrl':2}
        obj.cfilter = ['Result', 'Ref', 'Result']
        obj.write(filtered=True, append=False)
        written_data = _read(ofname)
        assert (
            written_data
            ==
            'Result,Ref,Result{0}30,4,30{0}40,5,40{0}'.format(lsep)
        )
        obj.reset_dfilter()
        # Test repeated columns with renamed header
        obj.reset_dfilter('c')
        obj.rfilter = {'Ctrl':2}
        obj.write(filtered=True, append=False, header=['A', 'B', 'C'])
        written_data = _read(ofname)
        assert written_data == 'A,B,C{0}2,4,30{0}2,5,40{0}'.format(lsep)
        obj.reset_dfilter('R')
        # Check saving unfiltered data column-sliced and also that
        # default for append argument is False
        obj.cfilter = 'Result'
        with putil.misc.TmpFile() as fname:
            obj.write(fname=fname, filtered='c')
            written_data = _read(fname)
        assert (
            written_data
            ==
            'Result{0}10{0}20{0}30{0}40{0}50{0}'.format(lsep)
        )
        # Check saving all data
        with putil.misc.TmpFile() as fname:
            obj.write(fname=fname, append=False)
            written_data = _read(fname)
        ref = (
            'Ctrl,Ref,Result{0}'
            '1,3,10{0}'
            '1,4,20{0}'
            '2,4,30{0}'
            '2,5,40{0}'
            '3,5,50{0}'.format(lsep)
        )
        assert written_data == ref
        obj.cfilter = ['Ctrl', 'Result']
        with putil.misc.TmpFile() as fname:
            obj.write(
                fname=fname,
                filtered=True,
                header=False,
                append=False
            )
            written_data = _read(fname)
        assert (
            written_data
            ==
            '1,10{0}1,20{0}2,30{0}2,40{0}3,50{0}'.format(lsep)
        )
        obj. cfilter = [0, 2]
        with putil.misc.TmpFile() as fname:
            obj.write(
                fname=fname,
                filtered=True,
                header=False,
                append=False
            )
            written_data = _read(fname)
        assert (
            written_data
            ==
            '1,10{0}1,20{0}2,30{0}2,40{0}3,50{0}'.format(lsep)
        )
        with putil.misc.TmpFile() as fname:
            obj.reset_dfilter()
            obj.rfilter = {'Result':[10, 30]}
            obj.write(fname=fname, filtered=True, header=True, append=False)
            obj.rfilter = {'Result':[20, 50]}
            obj.write(fname=fname, filtered=True, header=False, append=True)
            written_data = _read(fname)
        ref = (
            'Ctrl,Ref,Result{0}'
            '1,3,10{0}'
            '2,4,30{0}'
            '1,4,20{0}'
            '3,5,50{0}'.format(lsep)
        )
        assert written_data == ref
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            with putil.misc.TmpFile() as fname:
                obj.write(fname=fname)
                written_data = _read(fname)
        ref = "Ctrl,Ref,Result{0}2,'',30{0}2,5,40{0}3,5,50{0}".format(lsep)
        assert written_data == ref
        # Check file without header
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        ofname = fname
        with putil.misc.TmpFile() as fname:
            obj.cfilter = 1
            obj.write(fname=fname, filtered=True)
            written_data = _read(fname)
        assert written_data == '1{0}4{0}5{0}6{0}6{0}'.format(lsep)
        obj.rfilter = {0:1}
        with putil.misc.TmpFile() as fname:
            obj.cfilter = [1, 2]
            obj.write(fname=fname, filtered=True, header=False)
            written_data = _read(fname)
        assert written_data == '4,7{0}6,6{0}'.format(lsep)
        # Check None round trip
        with putil.misc.TmpFile(write_empty_cols) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.data() == [[1, None, 10], [1, 4, None]]
        with putil.misc.TmpFile() as fname:
            obj.write(fname, append=False)
            if sys.hexversion < 0x03000000:
                with open(fname, 'r') as fobj:
                    data = fobj.readlines()
            else:
                with open(fname, 'r', newline='') as fobj:
                    data = fobj.readlines()
        assert (
            data
            ==
            [
                'Col1,Col2,Col3{0}'.format(lsep),
                "1,'',10{0}".format(lsep),
                "1,4,''{0}".format(lsep)
            ]
        )

    @pytest.mark.csv_file
    def test_write_exceptions(self):
        """ Test write method exceptions """
        some_fname = os.path.join(os.path.abspath(os.sep), 'some', 'file')
        root_file = os.path.join(os.path.abspath(os.sep), 'test.csv')
        def mock_make_dir(fname):
            if fname == some_fname:
                raise IOError(
                    'File {0} could not be created'.format(some_fname),
                    'Permission denied'
                )
            elif fname == root_file:
                raise OSError(
                    'File {0} could not be created'.format(some_fname),
                    'Permission denied'
                )
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        putil.test.assert_exception(
            obj.write,
            {'fname':5},
            RuntimeError,
            'Argument `fname` is not valid'
        )
        for item in [8, []]:
            putil.test.assert_exception(
                obj.write,
                {'fname':some_fname, 'header':item},
                RuntimeError,
                'Argument `header` is not valid'
            )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'append':'a'},
            RuntimeError,
            'Argument `append` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'filtered':5},
            RuntimeError,
            'Argument `filtered` is not valid'
        )
        obj.rfilter = {'Result':100}
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'filtered':True},
            ValueError,
            'There is no data to save to file'
        )
        obj.reset_dfilter()
        with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir):
            putil.test.assert_exception(
                obj.write,
                {'fname':some_fname},
                OSError,
                'File {0} could not be created: Permission denied'.format(
                    some_fname
                )
            )
            putil.test.assert_exception(
                obj.write,
                {'fname':root_file},
                OSError,
                'File {0} could not be created: Permission denied'.format(
                    root_file
                )
            )

    def test_cfilter(self):
        """ Test cfilter property behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.cfilter is None
        obj.cfilter = 'Ctrl'
        assert obj.cfilter == ['Ctrl']

    @pytest.mark.csv_file
    def test_cfilter_exceptions(self):
        """ Test cfilter property exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        with pytest.raises(RuntimeError) as excinfo:
            obj.cfilter = 5.0
        assert (
            putil.test.get_exmsg(excinfo)
            ==
            'Argument `cfilter` is not valid'
        )
        with pytest.raises(ValueError) as excinfo:
            obj.cfilter = 'A'
        assert putil.test.get_exmsg(excinfo) == 'Column A not found'
        with pytest.raises(ValueError) as excinfo:
            obj.cfilter = 20
        assert putil.test.get_exmsg(excinfo) == 'Column 20 not found'
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        with pytest.raises(RuntimeError) as excinfo:
            obj.cfilter = 'A'
        assert putil.test.get_exmsg(excinfo) == 'Invalid column specification'

    def test_dfilter(self):
        """ Test dfilter property behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.dfilter == (None, None)
        obj.dfilter = None
        assert obj.dfilter == (None, None)
        obj.dfilter = (None, )
        assert obj.dfilter == (None, None)
        obj.dfilter = 'Ctrl'
        assert obj.dfilter == (None, ['Ctrl'])
        obj.dfilter = (None, 'Ctrl')
        assert obj.dfilter == (None, ['Ctrl'])
        obj.dfilter = ('Ctrl', None)
        assert obj.dfilter == (None, ['Ctrl'])
        obj.dfilter = {'Ref':5}
        assert obj.dfilter == ({'Ref':5}, None)
        obj.dfilter = ({'Ref':5}, None)
        assert obj.dfilter == ({'Ref':5}, None)
        obj.dfilter = (None, {'Ref':5})
        assert obj.dfilter == ({'Ref':5}, None)
        obj.dfilter = (['Ref'], {'Ref':5})
        assert obj.dfilter == ({'Ref':5}, ['Ref'])

    @pytest.mark.csv_file
    def test_dfilter_exceptions(self):
        """ Test dfilter property exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        msg = 'Argument `dfilter` is not valid'
        items = [
            True,
            (1, 2, 3),
            (True, 'A'),
            (True, ),
            (None, True),
            ('A', 'A'),
            ({'B':1}, {'C':5}),
            {2.0:5},
            ({2.0:5}, 'A'),
            (['A', True], {'A':1}),
            ('A', {}),
            ([], {'A':1}),
            ({}, []),
            {'dfilter':{'a':{'xx':2}}},
            {'dfilter':{'a':[3, {'xx':2}]}}
        ]
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.dfilter = item
            assert putil.test.get_exmsg(excinfo) == msg
        with pytest.raises(ValueError) as excinfo:
            obj.dfilter = {'aaa':5}
        assert putil.test.get_exmsg(excinfo) == 'Column aaa not found'
        with pytest.raises(ValueError) as excinfo:
            obj.dfilter = {10:5}
        assert putil.test.get_exmsg(excinfo) == 'Column 10 not found'
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        with pytest.raises(ValueError) as excinfo:
            obj.dfilter = {10:5}
        assert putil.test.get_exmsg(excinfo) == 'Column 10 not found'
        with pytest.raises(RuntimeError) as excinfo:
            obj.dfilter = {'10':5}
        assert putil.test.get_exmsg(excinfo) == msg

    def test_rfilter(self):
        """ Test rfilter property behavior """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            assert obj.rfilter is None
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':2, 'Ref':5})
        assert obj.data(filtered=True) == [[2, 5, 40]]
        obj.rfilter = {'Ctrl':[2, 3], 'Ref':5}
        assert obj.data(filtered=True) == [[2, 5, 40], [3, 5, 50]]
        obj.rfilter = {'Result':100}
        assert obj.data(filtered=True) == []
        obj.rfilter = {'Result':'hello'}
        assert obj.data(filtered=True) == []
        obj.rfilter = None
        assert obj.rfilter is None
        # Test filtering by strings
        with putil.misc.TmpFile(write_str_cols_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':'low'})
            assert obj.data(filtered=True) == [['low', 30]]
            obj.add_dfilter({'Ctrl':'nom'})
            assert obj.data(filtered=True) == [['nom', 10], ['low', 30]]
            obj.add_dfilter({'Ctrl':'high'})
            assert (
                obj.data(filtered=True)
                ==
                [['nom', 10], ['high', 20], ['low', 30]]
            )
        with putil.misc.TmpFile(write_no_header_file) as fname:
            obj = putil.pcsv.CsvFile(
                fname=fname, dfilter={0:3}, has_header=False
            )
            assert obj.data(filtered=True) == [[3, 6, 9]]
            obj.rfilter = {0:1, 2:6}
            assert obj.data(filtered=True) == [[1, 6, 6]]

    @pytest.mark.csv_file
    def test_rfilter_exceptions(self):
        """ Test rfilter property exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname)
        msg = 'Argument `rfilter` is not valid'
        items = [2.0, {5:True}, {'a':{'xx':2}}, {'a':[3, {'xx':2}]}]
        for item in items:
            with pytest.raises(RuntimeError) as excinfo:
                obj.rfilter = item
            assert putil.test.get_exmsg(excinfo) == msg
        with pytest.raises(ValueError) as excinfo:
            obj.rfilter = {}
        assert putil.test.get_exmsg(excinfo) == 'Argument `rfilter` is empty'
        with pytest.raises(ValueError) as excinfo:
            obj.rfilter = {'aaa':5}
        assert putil.test.get_exmsg(excinfo) == 'Column aaa not found'
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, has_header=False)
        with pytest.raises(RuntimeError) as excinfo:
            obj.rfilter = {'name':5}
        assert putil.test.get_exmsg(excinfo) == msg
        with pytest.raises(ValueError) as excinfo:
            obj.rfilter = {10:5}
        assert putil.test.get_exmsg(excinfo) == 'Column 10 not found'
        with pytest.raises(RuntimeError) as excinfo:
            obj.rfilter = {'a':5}
        assert putil.test.get_exmsg(excinfo) == msg

    @pytest.mark.csv_file
    def test_cannot_delete_attributes(self):
        """
        Test that del method raises an exception on all class attributes
        """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        with pytest.raises(AttributeError) as excinfo:
            del obj.cfilter
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.dfilter
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.rfilter
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
