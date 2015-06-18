# test_pcsv.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E0611,F0401,R0201,W0232

import mock
import os
import pytest
import sys
import tempfile

import putil.misc
import putil.pcsv
import putil.test
if sys.version_info.major == 2:
    from putil.compat2 import _read, _write
else:
    from putil.compat3 import _read, _write


###
# Tests for CsvFile
###
def write_file_empty(file_handle):
    _write(file_handle, '')


def write_cols_not_unique(file_handle):
    _write(file_handle, 'Col1,Col2,Col3,Col1')


def write_no_data(file_handle):
    _write(file_handle, 'Col1,Col2,Col3')


def write_data_start_file(file_handle):
    _write(file_handle, 'Ctrl,Ref,Result\n')
    _write(file_handle, '"a","+inf","real"\n')
    _write(file_handle, '"b","c","d"\n')
    _write(file_handle, '2,"",30\n')
    _write(file_handle, '2,5,40\n')
    _write(file_handle, '3,5,50\n')


def write_file(file_handle):
    _write(file_handle, 'Ctrl,Ref,Result\n')
    _write(file_handle, '1,3,10\n')
    _write(file_handle, '1,4,20\n')
    _write(file_handle, '2,4,30\n')
    _write(file_handle, '2,5,40\n')
    _write(file_handle, '3,5,50\n')


def write_str_cols_file(file_handle):
    _write(file_handle, 'Ctrl,Ref\n')
    _write(file_handle, '"nom",10\n')
    _write(file_handle, '"high",20\n')
    _write(file_handle, '"low",30\n')


class TestCsvFile(object):
    """ Tests for CsvFile class """
    def test_init_errors(self):
        """
        Test that the right exceptions are raised when wrong parameter is
        passed to argument fname
        """
        # pylint: disable=C0103
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
                'Column headers are not unique',
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
            'File `{0}` could not be found'.format(fname)
        )
        for extype, exmsg, fobj in func_pointers:
            with pytest.raises(extype) as excinfo:
                with putil.misc.TmpFile(fobj) as fname:
                    putil.pcsv.CsvFile(fname=fname)
            ref = (exmsg.format(fname) if '{0}' in exmsg else exmsg)
            assert putil.test.get_exmsg(excinfo) == ref

    def test_data_start(self):
        """ Test if the right row is picked for the data start """
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.data() == [[2, None, 30], [2, 5, 40], [3, 5, 50]]

    def test_dfilter_errors(self):
        """
        Test if the right exception is raised when parameter dfilter is of
        the wrong type or some columns in the filter specification are not
        present in CSV file header
        """
        with putil.misc.TmpFile(write_file) as fname:
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':'a'},
                RuntimeError,
                'Argument `dfilter` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':dict()},
                ValueError,
                'Argument `dfilter` is empty'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':{5:10}},
                RuntimeError,
                'Argument `dfilter` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':{'aaa':5}},
                ValueError,
                'Column aaa not found in header'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':{'a':{'xx':2}}},
                RuntimeError,
                'Argument `dfilter` is not valid'
            )
            putil.test.assert_exception(
                putil.pcsv.CsvFile,
                {'fname':fname, 'dfilter':{'a':[3, {'xx':2}]}},
                RuntimeError,
                'Argument `dfilter` is not valid'
            )

    def test_dfilter_works(self):
        """ Test if data filtering works """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            assert obj.dfilter is None
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':2, 'Ref':5})
        assert obj.data(filtered=True) == [[2, 5, 40]]
        obj.dfilter = {'Ctrl':[2, 3], 'Ref':5}
        assert obj.data(filtered=True) == [[2, 5, 40], [3, 5, 50]]
        obj.dfilter = {'Result':100}
        assert obj.data(filtered=True) == []
        obj.dfilter = {'Result':'hello'}
        assert obj.data(filtered=True) == []
        obj.dfilter = None
        assert obj.dfilter is None
        # Test filtering by strings
        with putil.misc.TmpFile(write_str_cols_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':'low'})
            assert obj.data(filtered=True) == [['low', 30]]
            obj.add_dfilter({'Ctrl':'nom'})
            assert obj.data(filtered=True) == [['nom', 10], ['low', 30]]
            obj.add_dfilter({'Ctrl':'high'})
            assert obj.data(filtered=True) == [
                ['nom', 10],
                ['high', 20],
                ['low', 30],
            ]

    def test_reset_dfilter_works(self):
        """ Test if data filter reset works """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Ctrl':2, 'Ref':5})
        assert obj.data(filtered=True) == [[2, 5, 40]]
        obj.reset_dfilter()
        assert obj.dfilter is None
        ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
        assert obj.data(filtered=True) == ref

    def test_add_dfilter_errors(self):
        """
        Test if the right exception is raised when parameter dfilter is of the
        wrong type or some columns in the filter specification are not present
        in CSV file header
        """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        putil.test.assert_exception(
            obj.add_dfilter,
            {'dfilter':'a'},
            RuntimeError,
            'Argument `dfilter` is not valid'
        )
        putil.test.assert_exception(
            obj.add_dfilter,
            {'dfilter':dict()},
            ValueError,
            'Argument `dfilter` is empty'
        )
        putil.test.assert_exception(
            obj.add_dfilter,
            {'dfilter':{'aaa':5}},
            ValueError,
            'Column aaa not found in header'
        )
        putil.test.assert_exception(
            obj.add_dfilter,
            {'dfilter':{'a':{'xx':2}}},
            RuntimeError,
            'Argument `dfilter` is not valid'
        )
        putil.test.assert_exception(
            obj.add_dfilter,
            {'dfilter':{'a':[3, {'xx':2}]}},
            RuntimeError,
            'Argument `dfilter` is not valid'
        )

    def test_add_dfilter_works(self):
        """ Test if adding filters to existing data filtering works """
        # No previous filter
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            obj.add_dfilter(None)
            ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
            assert obj.data(filtered=True) == ref
            obj.add_dfilter({'Ctrl':1})
            obj.add_dfilter({'Result':20})
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.reset_dfilter()
            obj.add_dfilter({'Result':20})
            assert obj.data(filtered=True) == [[1, 4, 20]]
            # Two single elements
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.add_dfilter({'Result':40})
            assert obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40]]
            # Single element to list
            obj.dfilter = {'Result':[10, 30]}
            assert obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30]]
            obj.add_dfilter({'Result':50})
            assert (
                obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30], [3, 5, 50]]
            )
            # List to list
            obj.dfilter = {'Result':[10, 20]}
            assert obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20]]
            obj.add_dfilter({'Result':[40, 50]})
            ref = [[1, 3, 10], [1, 4, 20], [2, 5, 40], [3, 5, 50]]
            assert obj.data(filtered=True) == ref
            # List to single element
            obj.dfilter = {'Result':20}
            assert obj.data(filtered=True) == [[1, 4, 20]]
            obj.add_dfilter({'Result':[40, 50]})
            assert (
                obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40], [3, 5, 50]]
            )

    def test_header_works(self):
        """ Test if header attribute works """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        assert obj.header == ['Ctrl', 'Ref', 'Result']

    def test_data_errors(self):
        """ Test if data() method raises the right exceptions """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        putil.test.assert_exception(
            obj.data,
            {'col':5},
            RuntimeError,
            'Argument `col` is not valid'
        )
        putil.test.assert_exception(
            obj.data,
            {'col':['a', 5]},
            RuntimeError,
            'Argument `col` is not valid'
        )
        putil.test.assert_exception(
            obj.data,
            {'col':'NotACol'},
            ValueError,
            'Column NotACol not found in header'
        )
        putil.test.assert_exception(
            obj.data,
            {'filtered':5},
            RuntimeError,
            'Argument `filtered` is not valid'
        )
        obj.data()
        obj.data(col=None, filtered=True)
        obj.data(col='Ctrl')
        obj.data(col=['Ctrl', 'Result'])

    def test_data_works(self):
        """ Test if data() method behaves properly """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
        assert obj.data() == ref
        assert obj.data(filtered=True) == [[1, 4, 20]]
        assert obj.data(col='Ref') == [[3], [4], [4], [5], [5]]
        assert obj.data(col='Ref', filtered=True) == [[4]]
        ref = [[1, 10], [1, 20], [2, 30], [2, 40], [3, 50]]
        assert obj.data(col=['Ctrl', 'Result']) == ref
        assert obj.data(col=['Ctrl', 'Result'], filtered=True) == [[1, 20]]

    def test_write_errors(self):
        """
        Test if write() method raises the right exceptions when its arguments
        are of the wrong type or are badly specified
        """
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
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'headers':'a'},
            RuntimeError,
            'Argument `headers` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'append':'a'},
            RuntimeError,
            'Argument `append` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'col':5},
            RuntimeError,
            'Argument `col` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'col':['a', 5]},
            RuntimeError,
            'Argument `col` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'filtered':5},
            RuntimeError,
            'Argument `filtered` is not valid'
        )
        putil.test.assert_exception(
            obj.write,
            {'fname':some_fname, 'col':'NotACol'},
            ValueError,
            'Column NotACol not found in header'
        )
        obj.dfilter = {'Result':100}
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

    def test_write_works(self):
        """ Test if write() method behaves properly """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
        with tempfile.NamedTemporaryFile() as fwobj:
            fname = fwobj.name
            obj.write(fname=fname, col='Result', filtered=True, append=False)
            written_data = _read(fname)
        assert written_data == 'Result\r\n10\r\n20\r\n30\r\n40\r\n50\r\n'
        with tempfile.NamedTemporaryFile() as fwobj:
            fname = fwobj.name
            obj.write(fname=fname, append=False)
            written_data = _read(fname)
        ref = (
            'Ctrl,Ref,Result\r\n'
            '1,3,10\r\n'
            '1,4,20\r\n'
            '2,4,30\r\n'
            '2,5,40\r\n'
            '3,5,50\r\n'
        )
        assert written_data == ref
        with tempfile.NamedTemporaryFile() as fwobj:
            fname = fwobj.name
            obj.write(
                fname=fname,
                col=['Ctrl', 'Result'],
                filtered=True,
                headers=False,
                append=False
            )
            written_data = _read(fname)
        assert written_data == '1,10\r\n1,20\r\n2,30\r\n2,40\r\n3,50\r\n'
        with tempfile.NamedTemporaryFile() as fwobj:
            fname = fwobj.name
            obj.reset_dfilter()
            obj.dfilter = {'Result':[10, 30]}
            obj.write(fname=fname, filtered=True, headers=True, append=False)
            obj.dfilter = {'Result':[20, 50]}
            obj.write(fname=fname, filtered=True, headers=False, append=True)
            written_data = _read(fname)
        ref = (
            'Ctrl,Ref,Result\r\n'
            '1,3,10\r\n'
            '2,4,30\r\n'
            '1,4,20\r\n'
            '3,5,50\r\n'
        )
        assert written_data == ref
        with putil.misc.TmpFile(write_data_start_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname)
            with tempfile.NamedTemporaryFile() as fwobj:
                fname = fwobj.name
                obj.write(fname=fname)
                written_data = _read(fname)
        ref = "Ctrl,Ref,Result\r\n2,'',30\r\n2,5,40\r\n3,5,50\r\n"
        assert written_data == ref

    def test_cannot_delete_attributes(self):
        """
        Test that del method raises an exception on all class attributes
        """
        with putil.misc.TmpFile(write_file) as fname:
            obj = putil.pcsv.CsvFile(fname=fname, dfilter={'Result':20})
        with pytest.raises(AttributeError) as excinfo:
            del obj.header
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.dfilter
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"


def test_write_function_errors():
    """
    Test if write() function raises the right exceptions when its arguments
    are of the wrong type or are badly specified
    """
    some_fname = os.path.join(os.path.abspath(os.sep), 'some', 'file')
    def mock_make_dir_io(fname):
        raise IOError(
            'File {0} could not be created'.format(fname),
            'Permission denied'
        )
    def mock_make_dir_os(fname):
        raise OSError(
            'File {0} could not be created'.format(fname),
            'Permission denied'
        )
    some_fname = os.path.join(os.path.abspath(os.sep), 'some', 'file')
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':5, 'data':[['Col1', 'Col2'], [1, 2]]},
        RuntimeError,
        'Argument `fname` is not valid'
    )
    putil.test.assert_exception(
        putil.pcsv.write,
        {
            'fname':some_fname,
            'data':[['Col1', 'Col2'], [1, 2]],
            'append':'a'
        },
        RuntimeError,
        'Argument `append` is not valid'
    )
    with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir_io):
        putil.test.assert_exception(
            putil.pcsv.write,
            {'fname':some_fname, 'data':[['Col1', 'Col2'], [1, 2]]},
            OSError,
            'File {0} could not be created: Permission denied'.format(
                some_fname
            )
        )
    with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir_os):
        putil.test.assert_exception(
            putil.pcsv.write,
            {'fname':some_fname, 'data':[['Col1', 'Col2'], [1, 2]]},
            OSError,
            'File {0} could not be created: Permission denied'.format(
                some_fname
            )
        )
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':'test.csv', 'data':[True, False]},
        RuntimeError,
        'Argument `data` is not valid'
    )
    putil.test.assert_exception(
        putil.pcsv.write,
        {'fname':'test.csv', 'data':[[]]},
        ValueError,
        'There is no data to save to file'
    )


def test_write_function_works():
    """ Test if write() method behaves properly """
    with tempfile.NamedTemporaryFile() as fwobj:
        fname = fwobj.name
        putil.pcsv.write(
            fname,
            [['Input', 'Output'], [1, 2], [3, 4]],
            append=False
        )
        written_data = _read(fname)
    assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n'
    with tempfile.NamedTemporaryFile() as fwobj:
        fname = fwobj.name
        putil.pcsv.write(
            fname,
            [['Input', 'Output'], [1, 2], [3, 4]],
            append=False
        )
        putil.pcsv.write(fname, [[5.0, 10]], append=True)
        written_data = _read(fname)
    assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n5.0,10\r\n'
