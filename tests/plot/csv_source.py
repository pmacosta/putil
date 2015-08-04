# csv_source.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,F0401
# pylint: disable=R0201,R0904,R0912,R0914,W0212,W0232,W0613

import numpy
import pytest
import sys

import putil.test
if sys.version_info.major == 2:
    from putil.compat2 import _write
else:
    from putil.compat3 import _write


###
# Helper functions
###
def write_csv_file(file_handle):
    _write(file_handle, 'Col1,Col2,Col3,Col4,Col5,Col6,Col7,Col8\n')
    _write(file_handle, '0,1,2,3,,5,1,7\n')
    _write(file_handle, '0,2,4,5,,4,2,6\n')
    _write(file_handle, '0,3,1,8,,3,3,5\n')
    _write(file_handle, '1,1,5,7,8,0,4,4\n')
    _write(file_handle, '1,2,3,7,9,7,5,3\n')


###
# Test classes
###
class TestCsvSource(object):
    """ Tests for CsvSource class """
    ### Private methods
    def test_str(self):
        """ Test __str__ method behavior """
        def fproc1(indep_var, dep_var):
            return indep_var*1e-3, dep_var+1
        def fproc2(indep_var, dep_var, par1, par2):
            return indep_var+par1, dep_var-par2
        with putil.misc.TmpFile(write_csv_file) as fname:
            # No rfilter
            obj = str(putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col3')
             )
            ref = (
                'File name: {}\n'
                'Row filter: None\n'
                'Independent column label: Col7\n'
                'Dependent column label: Col3\n'
                'Processing function: None\n'
                'Processing function extra arguments: None\n'
                'Independent variable minimum: -inf\n'
                'Independent variable maximum: +inf\n'
                'Independent variable: [ 1.0, 2.0, 3.0, 4.0, 5.0 ]\n'
                'Dependent variable: [ 2.0, 4.0, 1.0, 5.0, 3.0 ]'.format(fname)
            )
            assert obj == ref
            # rfilter
            obj = str(
                putil.plot.CsvSource(
                    fname=fname,
                    rfilter={'Col1':0},
                    indep_col_label='Col2',
                    dep_col_label='Col3'
                )
            )
            ref = (
                'File name: {}\n'
                'Row filter: \n'
                '   Col1: 0\n'
                'Independent column label: Col2\n'
                'Dependent column label: Col3\n'
                'Processing function: None\n'
                'Processing function extra arguments: None\n'
                'Independent variable minimum: -inf\n'
                'Independent variable maximum: +inf\n'
                'Independent variable: [ 1.0, 2.0, 3.0 ]\n'
                'Dependent variable: [ 2.0, 4.0, 1.0 ]'.format(fname)
            )
            assert obj == ref
            # fproc
            obj = str(putil.plot.CsvSource(
                fname=fname,
                rfilter={'Col1':0},
                indep_col_label='Col2',
                dep_col_label='Col3',
                indep_min=2e-3,
                indep_max=200,
                fproc=fproc1)
             )
            ref = (
                'File name: {}\n'
                'Row filter: \n'
                '   Col1: 0\n'
                'Independent column label: Col2\n'
                'Dependent column label: Col3\n'
                'Processing function: fproc1\n'
                'Processing function extra arguments: None\n'
                'Independent variable minimum: 0.002\n'
                'Independent variable maximum: 200\n'
                'Independent variable: [ 0.002, 0.003 ]\n'
                'Dependent variable: [ 5.0, 2.0 ]'.format(fname)
            )
            assert obj == ref
            # fproc_eargs
            obj = str(putil.plot.CsvSource(
                fname=fname,
                rfilter={'Col1':0},
                indep_col_label='Col2',
                dep_col_label='Col3',
                indep_min=-2,
                indep_max=200,
                fproc=fproc2,
                fproc_eargs={'par1':3, 'par2':4})
             )
            ref = (
                'File name: {}\n'
                'Row filter: \n'
                '   Col1: 0\n'
                'Independent column label: Col2\n'
                'Dependent column label: Col3\n'
                'Processing function: fproc2\n'
                'Processing function extra arguments: \n'
                '   par1: 3\n'
                '   par2: 4\n'
                'Independent variable minimum: -2\n'
                'Independent variable maximum: 200\n'
                'Independent variable: [ 4.0, 5.0, 6.0 ]\n'
                'Dependent variable: [ -2.0, 0.0, -3.0 ]'.format(fname)
            )
            assert obj == ref
            # indep_min set
            obj = str(putil.plot.CsvSource(
                fname=fname,
                rfilter={'Col1':0},
                indep_col_label='Col2',
                dep_col_label='Col3',
                indep_min=-2,
                fproc=fproc2,
                fproc_eargs={'par1':3, 'par2':4})
             )
            ref = (
                'File name: {}\n''Row filter: \n'
                '   Col1: 0\n'
                'Independent column label: Col2\n'
                'Dependent column label: Col3\n'
                'Processing function: fproc2\n'
                'Processing function extra arguments: \n'
                '   par1: 3\n'
                '   par2: 4\n'
                'Independent variable minimum: -2\n'
                'Independent variable maximum: +inf\n'
                'Independent variable: [ 4.0, 5.0, 6.0 ]\n'
                'Dependent variable: [ -2.0, 0.0, -3.0 ]'.format(fname)
            )
            assert obj == ref
            # indep_max set
            obj = str(putil.plot.CsvSource(
                fname=fname,
                rfilter={'Col1':0},
                indep_col_label='Col2',
                dep_col_label='Col3',
                indep_min=-2,
                indep_max=200,
                fproc=fproc2,
                fproc_eargs={'par1':3, 'par2':4})
             )
            ref = (
                'File name: {}\n''Row filter: \n'
                '   Col1: 0\n'
                'Independent column label: Col2\n'
                'Dependent column label: Col3\n'
                'Processing function: fproc2\n'
                'Processing function extra arguments: \n'
                '   par1: 3\n'
                '   par2: 4\n'
                'Independent variable minimum: -2\n'
                'Independent variable maximum: 200\n'
                'Independent variable: [ 4.0, 5.0, 6.0 ]\n'
                'Dependent variable: [ -2.0, 0.0, -3.0 ]'.format(fname)
            )
            assert obj == ref

    def test_complete(self):
        """ Test _complete method behavior """
        with putil.misc.TmpFile(write_csv_file) as fname:
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2'
            )
            obj._indep_var = None
            assert not obj._complete
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2'
            )
            assert obj._complete

    ### Properties
    def test_indep_max(self):
        """ Tests indep_max property behavior """
        items = [1, 2.0]
        with putil.misc.TmpFile(write_csv_file) as fname:
            # __init__ path
            for item in items:
                putil.plot.CsvSource(
                    fname=fname,
                    indep_col_label='Col7',
                    dep_col_label='Col2',
                    indep_max=item
                )
            # Managed attribute path
            obj = putil.plot.BasicSource(
                indep_var=numpy.array([1, 2, 3]),
                dep_var=numpy.array([10, 20, 30])
            )
            for item in items:
                obj.indep_max = item
                assert obj.indep_max == item

    @pytest.mark.csvsource
    def test_indep_max_exceptions(self):
        """ Tests indep_max property exceptions """
        msg = 'Argument `indep_max` is not valid'
        with putil.misc.TmpFile(write_csv_file) as fname:
            # __init__ path
            items = ['a', False]
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col7',
                        'dep_col_label':'Col2',
                        'indep_max':item
                    },
                    RuntimeError,
                    msg
                )
            # Managed attribute path
            obj = putil.plot.BasicSource(
                indep_var=numpy.array([1, 2, 3]),
                dep_var=numpy.array([10, 20, 30])
            )
            for item in items:
                with pytest.raises(RuntimeError) as excinfo:
                    obj.indep_max = item
                assert putil.test.get_exmsg(excinfo) == msg

    def test_indep_min(self):
        """ Tests indep_min property behavior """
        items = [1, 2.0]
        with putil.misc.TmpFile(write_csv_file) as fname:
            # __init__ path
            for item in items:
                putil.plot.CsvSource(
                    fname=fname,
                    indep_col_label='Col7',
                    dep_col_label='Col2',
                    indep_min=item
                )
            # Managed attribute path
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                indep_min=2.0
            )
            for item in items:
                obj.indep_min = item
                assert obj.indep_min == item

    @pytest.mark.csvsource
    def test_indep_min_exceptions(self):
        """ Tests indep_min property exceptions """
        msg = 'Argument `indep_min` is not valid'
        with putil.misc.TmpFile(write_csv_file) as fname:
            # __init__ path
            items = ['a', False]
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col7',
                        'dep_col_label':'Col2',
                        'indep_min':item
                    },
                    RuntimeError,
                    msg
                )
            # Managed attribute path
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                indep_min=2.0
            )
            for item in items:
                with pytest.raises(RuntimeError) as excinfo:
                    obj.indep_min = item
                assert putil.test.get_exmsg(excinfo) == msg

    @pytest.mark.csvsource
    def test_indep_min_greater_than_indep_max_exceptions(self):
        """
        Test if object behaves correctly when indep_min and indep_max
        are incongruous
        """
        msg = 'Argument `indep_min` is greater than argument `indep_max`'
        with putil.misc.TmpFile(write_csv_file) as fname:
            # Assign indep_min first
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                indep_min=0.5
            )
            with pytest.raises(ValueError) as excinfo:
                obj.indep_max = 0
            assert putil.test.get_exmsg(excinfo) == msg
            # Assign indep_max first
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                indep_max=10
            )
            with pytest.raises(ValueError) as excinfo:
                obj.indep_min = 50
            assert putil.test.get_exmsg(excinfo) == msg

    def test_fname(self):
        """ Test constructor fname argument behavior """
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2'
            )

    @pytest.mark.csvsource
    def test_fname_exceptions(self):
        """ Test constructor fname argument exceptions """
        # This assignment should raise an exception
        items = [5, None]
        for item in items:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {'fname':item, 'indep_col_label':'C7', 'dep_col_label':'C2'},
                RuntimeError,
                'Argument `fname` is not valid'
            )
        fname = 'nonexistent_fname.csv'
        putil.test.assert_exception(
            putil.plot.CsvSource,
            {'fname':fname, 'indep_col_label':'Col7', 'dep_col_label':'Col2'},
            OSError,
            'File {} could not be found'.format(fname)
        )

    @pytest.mark.csvsource
    def test_indep_col_label_exceptions(self):
        """ Test constructor indep_col_label argument exceptions """
        items = [None, 5]
        with putil.misc.TmpFile(write_csv_file) as fname:
            # These assignments should raise an exception
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':item,
                        'dep_col_label':'Col2'
                    },
                    RuntimeError,
                    'Argument `indep_col_label` is not valid'
                )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col99',
                    'dep_col_label':'Col2'
                },
                ValueError,
                'Column Col99 (independent column label) could not be found '
                'in comma-separated file {0} header'.format(fname)
            )

    @pytest.mark.csvsource
    def test_dep_col_label_exceptions(self):
        """ Test constructor indep_col_label argument exceptions """
        items = [None, 5]
        with putil.misc.TmpFile(write_csv_file) as fname:
            # This assignment should raise an exception
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col7',
                        'dep_col_label':item
                    },
                    RuntimeError,
                    'Argument `dep_col_label` is not valid'
                )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col99'
                },
                ValueError,
                'Column Col99 (dependent column label) could not be found in '
                'comma-separated file {0} header'.format(fname)
            )

    @pytest.mark.csvsource
    def test_empty_indep_var_after_filter_exceptions(self):
        """ Test empty independent variable after rfilter exceptions """
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':10}
                },
                ValueError,
                'Filtered independent variable is empty'
            )

    @pytest.mark.csvsource
    def test_empty_dep_var_after_filter_exceptions(self):
        """ Test empty dependent variable after rfilter exceptions """
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col5', 'rfilter':{'Col1':0}
                },
                ValueError,
                'Filtered dependent variable is empty'
            )

    def test_data_reversed(self):
        """ Test reordering when independent variable in descending order """
        with putil.misc.TmpFile(write_csv_file) as fname:
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col6',
                dep_col_label='Col3',
                rfilter={'Col1':0}
            )
        assert (obj.indep_var == numpy.array([3, 4, 5])).all()
        assert (obj.dep_var == numpy.array([1, 4, 2])).all()

    def test_fproc(self):
        """ Test fproc property behavior """
        def fproc1(indep_var, dep_var, indep_offset, dep_offset):
            return indep_var+indep_offset, dep_var+dep_offset
        def fproc2(*args):
            return numpy.array([1]), numpy.array([1])
        def fproc3(*args, **kwargs):
            return numpy.array([1, 2, 3, 4, 5]), numpy.array([1, 2, 3, 1, 2])
        def fproc4(indep_var, dep_var):
            return [numpy.array([1, 2]), numpy.array([1, 2])]
        def fproc7(indep_var, dep_var):
            return [numpy.array([1, 2]), numpy.array([3, 1])]
        with putil.misc.TmpFile(write_csv_file) as fname:
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col2',
                dep_col_label='Col3',
                rfilter={'Col1':0},
                fproc=fproc1,
                fproc_eargs={'indep_offset':3, 'dep_offset':100}
            )
        assert (obj.indep_var == numpy.array([4, 5, 6])).all()
        assert (obj.dep_var == numpy.array([102, 104, 101])).all()
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                fproc=fproc2
            )
            putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2',
                fproc=fproc3
            )
            putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col2',
                dep_col_label='Col3',
                rfilter={'Col1':0},
                fproc=fproc4
            )
            putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col2',
                dep_col_label='Col3',
                rfilter={'Col1':0},
                fproc=fproc7
            )

    @pytest.mark.csvsource
    def test_fproc_exceptions(self):
        """ Test fproc property exceptions """
        def fproc1():
            return numpy.array([1]), numpy.array([1])
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'fproc':5
                },
                RuntimeError,
                'Argument `fproc` is not valid'
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'fproc':fproc1
                },
                ValueError,
                'Argument `fproc` (function fproc1) does not have at least '
                '2 arguments'
            )

    def test_fproc_eargs(self):
        """ Test fprog_eargs property behavior """
        def fproc3(indep_var, dep_var, **kwargs):
            return [numpy.array([1, 2]), numpy.array([1, 2])]
        items = [None, {'arg1':23}, {'par99':5}]
        with putil.misc.TmpFile(write_csv_file) as fname:
            for item in items:
                putil.plot.CsvSource(
                    fname=fname,
                    indep_col_label='Col7',
                    dep_col_label='Col2',
                    fproc=fproc3,
                    fproc_eargs=item
                )

    @pytest.mark.csvsource
    def test_fproc_eargs_exceptions(self):
        """ Test fprog_eargs property exceptions """
        def fproc1(indep_var, dep_var):
            return [numpy.array([1, 2]), numpy.array([1, 2])]
        def fproc2(indep_var, dep_var, par1, par2):
            return [numpy.array([1, 2]), numpy.array([1, 2])]
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'fproc_eargs':5
                },
                RuntimeError,
                'Argument `fproc_eargs` is not valid'
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'fproc':fproc1,
                    'fproc_eargs':{'par1':5}
                },
                ValueError,
                'Extra argument `par1` not found in argument `fproc` '
                '(function fproc1) definition'
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'fproc':fproc2,
                    'fproc_eargs':{'par3':5}
                },
                ValueError,
                'Extra argument `par3` not found in argument `fproc` '
                '(function fproc2) definition'
            )

    @pytest.mark.csvsource
    def test_data_processing_exceptions(self):
        """ Test data processing output exceptions """
        def fproc1(indep_var, dep_var):
            return True
        def fproc2(indep_var, dep_var):
            return [numpy.array([1, 2])]
        def fproc4(indep_var, dep_var):
            return [5, numpy.array([1, 2])]
        def fproc5(indep_var, dep_var):
            return [numpy.array([3, 2, 1]), numpy.array([1, 2, 3])]
        def fproc6(indep_var, dep_var):
            return [numpy.array([1, 2]), 6]
        def fproc8(indep_var, dep_var):
            return [numpy.array([]), numpy.array([3, 1])]
        def fproc9(indep_var, dep_var):
            return [numpy.array([1, 3]), numpy.array([])]
        def fproc10(indep_var, dep_var):
            return [numpy.array([None, None]), numpy.array([3, 1])]
        def fproc11(indep_var, dep_var):
            return [numpy.array([1, 3]), numpy.array([None, None])]
        def fproc12(indep_var, dep_var):
            return [numpy.array([1, 3]), numpy.array([1, 2, 3])]
        def fproc13(indep_var, dep_var, par1):
            raise RuntimeError('Test exception message #1')
        def fproc14(indep_var, dep_var, par1=None):
            raise RuntimeError('Test exception message #2')
        with putil.misc.TmpFile(write_csv_file) as fname:
            # These assignments should raise an exception
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc1
                },
                TypeError,
                'Argument `fproc` (function fproc1) return value is not valid'
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc2
                },
                RuntimeError,
                'Argument `fproc` (function fproc2) returned an illegal '
                'number of values'
            )
            items = [fproc4, fproc5]
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col2',
                        'dep_col_label':'Col3',
                        'rfilter':{'Col1':0},
                        'fproc':item
                    },
                    TypeError,
                    'Processed independent variable is not valid'
                )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc6
                },
                TypeError,
                'Processed dependent variable is not valid'
            )
            items = [fproc8, fproc10]
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col2',
                        'dep_col_label':'Col3',
                        'rfilter':{'Col1':0},
                        'fproc':item
                    },
                    ValueError,
                    'Processed independent variable is empty'
                )
            items = [fproc9, fproc11]
            for item in items:
                putil.test.assert_exception(
                    putil.plot.CsvSource,
                    {
                        'fname':fname,
                        'indep_col_label':'Col2',
                        'dep_col_label':'Col3',
                        'rfilter':{'Col1':0},
                        'fproc':item
                    },
                    ValueError,
                    'Processed dependent variable is empty'
                )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc12
                },
                ValueError,
                'Processed independent and dependent variables are of '
                'different length'
            )
            msg = (
                'Processing function fproc13 raised an exception when '
                    'called with the following arguments:\n'
                'indep_var: [ 1.0, 2.0, 3.0 ]\n'
                'dep_var: [ 1.0, 2.0, 3.0 ]\n'
                'fproc_eargs: \n'
                '   par1: 13\n'
                'Exception error: Test exception message #1'
            )

            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc13,
                    'fproc_eargs':{'par1':13}
                },
                RuntimeError,
                msg
            )
            msg = (
                'Processing function fproc14 raised an exception when '
                    'called with the following arguments:\n'
                'indep_var: [ 1.0, 2.0, 3.0 ]\n'
                'dep_var: [ 1.0, 2.0, 3.0 ]\n'
                'fproc_eargs: None\n'
                'Exception error: Test exception message #2'
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc14, 'fproc_eargs':{}
                },
                RuntimeError,
                msg
            )
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col2',
                    'dep_col_label':'Col3',
                    'rfilter':{'Col1':0},
                    'fproc':fproc14
                },
                RuntimeError,
                msg
            )

    def test_rfilter(self):
        """ Test constructor rfilter argument behavior """
        items = [None, {'Col1':0}]
        for item in items:
            with putil.misc.TmpFile(write_csv_file) as fname:
                putil.plot.CsvSource(
                    fname=fname,
                    indep_col_label='Col7',
                    dep_col_label='Col2',
                    rfilter=item
                )

    @pytest.mark.csvsource
    def test_rfilter_exceptions(self):
        """ Test constructor rfilter argument exceptions """
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'rfilter':5},
                RuntimeError,
                'Argument `rfilter` is not valid'
            )
        with putil.misc.TmpFile(write_csv_file) as fname:
            putil.test.assert_exception(
                putil.plot.CsvSource,
                {
                    'fname':fname,
                    'indep_col_label':'Col7',
                    'dep_col_label':'Col2',
                    'rfilter':{'Col99':500}
                },
                ValueError,
                'Column Col99 in row filter not found in '
                'comma-separated file {} header'.format(fname)
            )

    @pytest.mark.csvsource
    def test_cannot_delete_attributes_exceptions(self):
        """
        Test that del method raises an exception on all class attributes
        """
        with putil.misc.TmpFile(write_csv_file) as fname:
            obj = putil.plot.CsvSource(
                fname=fname,
                indep_col_label='Col7',
                dep_col_label='Col2'
            )
            with pytest.raises(AttributeError) as excinfo:
                del obj.dep_col_label
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.dep_var
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.fname
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.fproc
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.fproc_eargs
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.indep_col_label
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.indep_max
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.indep_min
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.indep_var
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
            with pytest.raises(AttributeError) as excinfo:
                del obj.rfilter
            assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
