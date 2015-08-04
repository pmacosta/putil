# test_ptypes.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111

import numpy
import sys

import putil.ptypes
import putil.test


###
# Test functions
###
def test_color_space_option_contract():
    """ Tests for LineStyleOption pseudo-type """
    putil.test.assert_exception(
        putil.ptypes.color_space_option,
        {'obj':5},
        ValueError,
        (
            '[START CONTRACT MSG: color_space_option]Argument '
            '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
        )
    )
    putil.test.assert_exception(
        putil.ptypes.color_space_option,
        {'obj':'x'},
        ValueError,
        (
            "[START CONTRACT MSG: color_space_option]Argument "
            "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
            "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
            "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
            "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]"
        )
    )
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
        putil.test.assert_exception(
            putil.ptypes.csv_col_filter,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: csv_col_filter]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [None, 1, 'a', [1, 2], ['a']]
    for item in items:
        putil.ptypes.csv_col_filter(item)


def test_csv_col_sort_contract():
    """ Test CsvColSort pseudo-type """
    items = [
        True, None, ['a', None], {(1, 2):'A'}, {'a':True}, {0:'hello'}, []
    ]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.csv_col_sort,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: csv_col_sort]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
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
        putil.test.assert_exception(
            putil.ptypes.csv_data_filter,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: csv_data_filter]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
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
        putil.test.assert_exception(
            putil.ptypes.csv_filtered,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: csv_filtered]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
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
        putil.test.assert_exception(
            putil.ptypes.csv_row_filter,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: csv_row_filter]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    putil.test.assert_exception(
        putil.ptypes.csv_row_filter,
        {'obj':{}},
        ValueError,
        (
            '[START CONTRACT MSG: csv_row_filter]Argument '
            '`*[argument_name]*` is empty[STOP CONTRACT MSG]'
        )
    )
    items = [None, {'x':5}]
    for item in items:
        putil.ptypes.csv_row_filter(item)


def test_engineering_notation_number():
    """ Test EngineeringNotationNumber pseudo-type """
    items = ['3.12b', 'f', 'a1b', '   +  123.45f  ']
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.engineering_notation_number,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: engineering_notation_number]'
                'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = ['   +123.45f  ', '   -0  ']
    for item in items:
        putil.ptypes.engineering_notation_number(item)


def test_engineering_notation_suffix():
    """ Test EngineeringNotationSuffix pseudo-type """
    putil.test.assert_exception(
        putil.ptypes.engineering_notation_suffix,
        {'obj':'b'},
        ValueError,
        (
            '[START CONTRACT MSG: engineering_notation_suffix]'
            'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'
        )
    )
    putil.ptypes.engineering_notation_suffix('u')


def test_file_name_contract():
    """ Test for file_name custom contract """
    @putil.pcontracts.contract(sfn='file_name')
    def func(sfn):
        """ Sample function to test file_name custom contract """
        return sfn
    items = [3, 'test\0']
    for item in items:
        putil.test.assert_exception(
            func, {'sfn':item}, RuntimeError, 'Argument `sfn` is not valid'
        )
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
        putil.test.assert_exception(
            func, {'sfn':item}, RuntimeError, 'Argument `sfn` is not valid'
        )
    putil.test.assert_exception(
        func,
        {'sfn':'_file_does_not_exist'},
        OSError,
        'File _file_does_not_exist could not be found'
    )
    # Test with Python executable (should be portable across systems)
    func(sys.executable)


def test_function_contract():
    """ Tests for Function pseudo-type """
    def func1():
        pass
    putil.test.assert_exception(
        putil.ptypes.function,
        {'obj':'a'},
        ValueError,
        (
            '[START CONTRACT MSG: function]Argument `*[argument_name]*` '
            'is not valid[STOP CONTRACT MSG]'
        )
    )
    items = (func1, None)
    for item in items:
        putil.ptypes.function(item)


def test_increasing_real_numpy_vector_contract():
    """ Tests for IncreasingRealNumpyVector pseudo-type """
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
        putil.test.assert_exception(
            putil.ptypes.increasing_real_numpy_vector,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [
        numpy.array([1, 2, 3]),
        numpy.array([10.0, 12.1, 12.5]),
        numpy.array([10.0])
    ]
    for item in items:
        putil.ptypes.increasing_real_numpy_vector(item)


def test_interpolation_option_contract():
    """ Tests for InterpolationOption pseudo-type """
    putil.test.assert_exception(
        putil.ptypes.interpolation_option,
        {'obj':5},
        ValueError,
        (
            '[START CONTRACT MSG: interpolation_option]Argument '
            '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
        )
    )
    putil.test.assert_exception(
        putil.ptypes.interpolation_option,
        {'obj':'x'},
        ValueError,
        (
            "[START CONTRACT MSG: interpolation_option]Argument "
            "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
            "'LINREG'] (case insensitive)[STOP CONTRACT MSG]"
        )
    )
    putil.ptypes.interpolation_option(None)
    for item in ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']:
        putil.ptypes.interpolation_option(item)
        putil.ptypes.interpolation_option(item.lower())


def test_line_style_option_contract():
    """ Tests for LineStyleOption pseudo-type """
    putil.test.assert_exception(
        putil.ptypes.line_style_option,
        {'obj':5},
        ValueError,
        (
            '[START CONTRACT MSG: line_style_option]Argument '
            '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
        )
    )
    putil.test.assert_exception(
        putil.ptypes.line_style_option,
        {'obj':'x'},
        ValueError,
        (
            "[START CONTRACT MSG: line_style_option]Argument "
            "`*[argument_name]*` is not one of ['-', '--', '-.', "
            "':'][STOP CONTRACT MSG]"
        )
    )
    putil.ptypes.line_style_option(None)
    for item in ['-', '--', '-.', ':']:
        putil.ptypes.line_style_option(item)


def test_non_negative_integer():
    """ Test PosInteger pseudo-type """
    items = ['b', -3, 5.2]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.non_negative_integer,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: non_negative_integer]'
                'Argument `*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [0, 2]
    for item in items:
        putil.ptypes.non_negative_integer(item)


def test_offset_range_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    items = ['a', [1, 2, 3], False, -0.1, -1.1]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.offset_range,
            {'obj':item},
            ValueError,
            ('[START CONTRACT MSG: offset_range]Argument `*[argument_name]*` '
             'is not valid[STOP CONTRACT MSG]')
        )
    items = [0, 0.5, 1]
    for item in items:
        putil.ptypes.offset_range(item)


def test_positive_real_num_contract():
    """ Tests for PositiveRealNumber pseudo-type """
    items = ['a', [1, 2, 3], False, -0.1, -2.0]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.positive_real_num,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: positive_real_num]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [1, 2.0]
    for item in items:
        putil.ptypes.positive_real_num(item)


def test_real_num_contract():
    """ Tests for RealNumber pseudo-type """
    items = ['a', [1, 2, 3], False]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.real_num,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
                'is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [1, 2.0]
    for item in items:
        putil.ptypes.real_num(item)


def test_real_numpy_vector_contract():
    """ Tests for RealNumpyVector pseudo-type """
    items = [
        'a',
        [1, 2, 3],
        numpy.array([]),
        numpy.array([[1, 2, 3], [4, 5, 6]]),
        numpy.array(['a', 'b']),
    ]
    for item in items:
        putil.test.assert_exception(
            putil.ptypes.real_numpy_vector,
            {'obj':item},
            ValueError,
            (
                '[START CONTRACT MSG: real_numpy_vector]Argument '
                '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
            )
        )
    items = [
        numpy.array([1, 2, 3]),
        numpy.array([10.0, 8.0, 2.0]),
        numpy.array([10.0])
    ]
    for item in items:
        putil.ptypes.real_numpy_vector(item)
