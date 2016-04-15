# test_ptypes.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,W0108

# Standard library imports
import sys
import numpy
# Putil imports
import putil.ptypes
from putil.test import AE, AI


###
# Global variables
###
emsg = lambda msg: (
    '[START CONTRACT MSG: {0}]Argument `*[argument_name]*` '
    'is not valid[STOP CONTRACT MSG]'.format(msg)
)


###
# Helper functions
###
def check_contract(obj, name, value):
    AE(obj, ValueError, emsg(name), obj=value)


###
# Test functions
###
def test_color_space_option_contract():
    """ Tests for LineStyleOption pseudo-type """
    obj = putil.ptypes.color_space_option
    check_contract(obj, 'color_space_option', 5)
    exmsg = (
        "[START CONTRACT MSG: color_space_option]Argument "
        "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
        "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
        "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
        "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]"
    )
    AE(obj, ValueError, exmsg, obj='x')
    for item in [
            'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
            'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
            'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr',
            'YlOrRd']:
        putil.ptypes.color_space_option(item)


def test_csv_col_filter_contract():
    """ Test CsvColFilter pseudo-type """
    items = [True, 1.0, [], [1, True, 3], ['a', 'b', True]]
    for item in items:
        check_contract(putil.ptypes.csv_col_filter, 'csv_col_filter', item)
    items = [None, 1, 'a', [1, 2], ['a']]
    for item in items:
        putil.ptypes.csv_col_filter(item)


def test_csv_col_sort_contract():
    """ Test CsvColSort pseudo-type """
    items = [
        True, None, ['a', None], {(1, 2):'A'}, {'a':True}, {0:'hello'}, []
    ]
    for item in items:
        check_contract(putil.ptypes.csv_col_sort, 'csv_col_sort', item)
    items = [
        1,
        'a',
        {'a':'D'},
        {0:'d'},
        {1:'a'},
        [1, 'a'],
        [1, 'a', {'b':'d'}, {0:'A'}]
    ]
    for item in items:
        putil.ptypes.csv_col_sort(item)


def test_csv_data_filter_contract():
    """ Test CsvDataFilter pseudo-type """
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
        check_contract(putil.ptypes.csv_data_filter, 'csv_data_filter', item)
    items = [
        None,
        (None, ),
        (None, None),
        1,
        'A',
        ['B', 1],
        {'A':1},
        {'A':1, 'B':2}
    ]
    for item in items:
        putil.ptypes.csv_data_filter(item)


def test_csv_filtered_contract():
    """ Test CsvFiltered pseudo-type """
    for item in [5, 'BC']:
        check_contract(putil.ptypes.csv_filtered, 'csv_filtered', item)
    for item in [True, False, 'B', 'b', 'C', 'c', 'R', 'r', 'N', 'n']:
        putil.ptypes.csv_filtered(item)


def test_csv_row_filter_contract():
    """ Test CsvRowFilter pseudo-type """
    items = [
        'a',
        {5.0:10},
        {'a':{'xx':2}},
        {'a':[3, {'xx':2}]},
        {'b':True}
    ]
    for item in items:
        check_contract(putil.ptypes.csv_row_filter, 'csv_row_filter', item)
    exmsg = (
        '[START CONTRACT MSG: csv_row_filter]Argument '
        '`*[argument_name]*` is empty[STOP CONTRACT MSG]'
    )
    AE(putil.ptypes.csv_row_filter, ValueError, exmsg, obj={})
    items = [None, {'x':5}]
    for item in items:
        putil.ptypes.csv_row_filter(item)


def test_engineering_notation_number():
    """ Test EngineeringNotationNumber pseudo-type """
    obj = putil.ptypes.engineering_notation_number
    items = ['3.12b', 'f', 'a1b', '   +  123.45f  ']
    for item in items:
        check_contract(obj, 'engineering_notation_number', item)
    items = ['   +123.45f  ', '   -0  ']
    for item in items:
        obj(item)


def test_engineering_notation_suffix():
    """ Test EngineeringNotationSuffix pseudo-type """
    obj = putil.ptypes.engineering_notation_suffix
    check_contract(obj, 'engineering_notation_suffix', 'b')
    obj('u')


def test_file_name_contract():
    """ Test for file_name custom contract """
    @putil.pcontracts.contract(sfn='file_name')
    def func(sfn):
        """ Sample function to test file_name custom contract """
        return sfn
    items = [3, 'test\0']
    for item in items:
        AI(func, 'sfn', sfn=item)
    func('some_file.txt')
    # Test with Python executable (should be portable across systems), file
    # should be valid although not having permissions to write it
    func(sys.executable)


def test_file_name_exists_contract():
    """ Test for file_name_exists custom contract """
    @putil.pcontracts.contract(sfn='file_name_exists')
    def func(sfn):
        """ Sample function to test file_name_exists custom contract """
        return sfn
    items = [3, 'test\0']
    for item in items:
        AI(func, 'sfn', sfn=item)
    exmsg = 'File _file_does_not_exist could not be found'
    AE(func, OSError, exmsg, sfn='_file_does_not_exist')
    # Test with Python executable (should be portable across systems)
    func(sys.executable)


def test_function_contract():
    """ Tests for Function pseudo-type """
    def func1():
        pass
    check_contract(putil.ptypes.function, 'function', 'a')
    items = (func1, None)
    for item in items:
        putil.ptypes.function(item)


def test_increasing_real_numpy_vector_contract():
    """ Tests for IncreasingRealNumpyVector pseudo-type """
    obj = putil.ptypes.increasing_real_numpy_vector
    items = [
        'a',
        [1, 2, 3],
        numpy.array([]),
        numpy.array([[1, 2, 3], [4, 5, 6]]),
        numpy.array(['a', 'b']),
        numpy.array([1, 0, -3]),
        numpy.array([10.0, 8.0, 2.0])
    ]
    for item in items:
        check_contract(obj, 'increasing_real_numpy_vector', item)
    items = [
        numpy.array([1, 2, 3]),
        numpy.array([10.0, 12.1, 12.5]),
        numpy.array([10.0])
    ]
    for item in items:
        obj(item)


def test_interpolation_option_contract():
    """ Tests for InterpolationOption pseudo-type """
    obj = putil.ptypes.interpolation_option
    check_contract(obj, 'interpolation_option', 5)
    exmsg = (
        "[START CONTRACT MSG: interpolation_option]Argument "
        "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
        "'LINREG'] (case insensitive)[STOP CONTRACT MSG]"
    )
    AE(obj, ValueError, exmsg, obj='x')
    obj(None)
    for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']:
        obj(item)
        obj(item.lower())


def test_line_style_option_contract():
    """ Tests for LineStyleOption pseudo-type """
    check_contract(putil.ptypes.line_style_option, 'line_style_option', 5)
    exmsg = (
        "[START CONTRACT MSG: line_style_option]Argument "
        "`*[argument_name]*` is not one of ['-', '--', '-.', "
        "':'][STOP CONTRACT MSG]"
    )
    AE(putil.ptypes.line_style_option, ValueError, exmsg, obj='x')
    putil.ptypes.line_style_option(None)
    for item in ['-', '--', '-.', ':']:
        putil.ptypes.line_style_option(item)


def test_non_negative_integer():
    """ Test PosInteger pseudo-type """
    obj = putil.ptypes.non_negative_integer
    items = ['b', True, -3, 5.2]
    for item in items:
        check_contract(obj, 'non_negative_integer', item)
    items = [0, 2]
    for item in items:
        obj(item)


def test_offset_range_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    items = ['a', [1, 2, 3], False, -0.1, -1.1]
    for item in items:
        check_contract(putil.ptypes.offset_range, 'offset_range', item)
    items = [0, 0.5, 1]
    for item in items:
        putil.ptypes.offset_range(item)


def test_positive_real_num_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    obj = putil.ptypes.positive_real_num
    items = ['a', [1, 2, 3], False, -0.1, -2.0]
    for item in items:
        check_contract(obj, 'positive_real_num', item)
    items = [1, 2.0]
    for item in items:
        obj(item)


def test_real_num_contract():
    """ Tests for RealNumber pseudo-type """
    items = ['a', [1, 2, 3], False]
    for item in items:
        check_contract(putil.ptypes.real_num, 'real_num', item)
    items = [1, 2.0]
    for item in items:
        putil.ptypes.real_num(item)


def test_real_numpy_vector_contract():
    """ Tests for RealNumpyVector pseudo-type """
    obj = putil.ptypes.real_numpy_vector
    items = [
        'a',
        [1, 2, 3],
        numpy.array([]),
        numpy.array([[1, 2, 3], [4, 5, 6]]),
        numpy.array(['a', 'b']),
    ]
    for item in items:
        check_contract(obj, 'real_numpy_vector', item)
    items = [
        numpy.array([1, 2, 3]),
        numpy.array([10.0, 8.0, 2.0]),
        numpy.array([10.0])
    ]
    for item in items:
        obj(item)
