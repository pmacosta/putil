# ccontracts.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,W0212,W0232,W0613

import numpy

import putil.plot
import putil.test


###
# Test classes
###
class TestContracts(object):
    """ Test for ccontract sub-module """
    def test_real_num_contract(self):
        """ Tests for RealNumber pseudo-type """
        items = ['a', [1, 2, 3], False]
        for item in items:
            putil.test.assert_exception(
                putil.plot.real_num,
                {'obj':'a'},
                ValueError,
                ('[START CONTRACT MSG: real_num]Argument `*[argument_name]*` '
                 'is not valid[STOP CONTRACT MSG]')
            )
        items = [-1, 1, 2.0]
        for item in items:
            putil.plot.real_num(item)

    def test_positive_real_num_contract(self):
        """ Tests for PositiveRealNumber pseudo-type """
        items = ['a', [1, 2, 3], False, -1, -2.0]
        for item in items:
            putil.test.assert_exception(
                putil.plot.positive_real_num,
                {'obj':'a'},
                ValueError,
                (
                    '[START CONTRACT MSG: positive_real_num]Argument '
                    '`*[argument_name]*` is not valid[STOP CONTRACT MSG]'
                )
            )
        items = [1, 2.0]
        for item in items:
            putil.plot.positive_real_num(item)

    def test_offset_range_contract(self):
        """ Tests for PositiveRealNumber pseudo-type """
        items = ['a', [1, 2, 3], False, -0.1, -1.1]
        for item in items:
            putil.test.assert_exception(
                putil.plot.offset_range,
                {'obj':item},
                ValueError,
                ('[START CONTRACT MSG: offset_range]Argument '
                 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
            )
        items = [0, 0.5, 1]
        for item in items:
            putil.plot.offset_range(item)

    def test_function_contract(self):
        """ Tests for Function pseudo-type """
        def func1():
            pass
        putil.test.assert_exception(
            putil.plot.function,
            {'obj':'a'},
            ValueError,
            ('[START CONTRACT MSG: function]Argument `*[argument_name]*` '
             'is not valid[STOP CONTRACT MSG]')
        )
        items = [None, func1]
        for item in items:
            putil.plot.function(item)

    def test_real_numpy_vector_contract(self):
        """ Tests for RealNumpyVector pseudo-type """
        items = [
            'a',
            [1, 2, 3],
            numpy.array([]),
            numpy.array([[1, 2, 3], [4, 5, 6]]),
            numpy.array(['a', 'b'])
        ]
        for item in items:
            putil.test.assert_exception(
                putil.plot.real_numpy_vector,
                {'obj':item},
                ValueError,
                ('[START CONTRACT MSG: real_numpy_vector]Argument '
                 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
            )
        items = [
            numpy.array([1, 2, 3]),
            numpy.array([10.0, 8.0, 2.0]),
            numpy.array([10.0])
        ]
        for item in items:
            putil.plot.real_numpy_vector(item)

    def test_increasing_real_numpy_vector_contract(self):
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
                putil.plot.increasing_real_numpy_vector,
                {'obj':item},
                ValueError,
                ('[START CONTRACT MSG: increasing_real_numpy_vector]Argument '
                 '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
            )
        items = [
            numpy.array([1, 2, 3]),
            numpy.array([10.0, 12.1, 12.5]),
            numpy.array([10.0])
        ]
        for item in items:
            putil.plot.increasing_real_numpy_vector(item)

    def test_interpolation_option_contract(self):
        """ Tests for InterpolationOption pseudo-type """
        putil.test.assert_exception(
            putil.plot.interpolation_option,
            {'obj':5},
            ValueError,
            ('[START CONTRACT MSG: interpolation_option]Argument '
             '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
        )
        putil.test.assert_exception(
            putil.plot.interpolation_option,
            {'obj':'x'},
            ValueError,
            ("[START CONTRACT MSG: interpolation_option]Argument "
             "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
             "'LINREG'] (case insensitive)[STOP CONTRACT MSG]")
        )
        putil.plot.interpolation_option(None)
        items = ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']
        for item in items:
            putil.plot.interpolation_option(item)
            putil.plot.interpolation_option(item.lower())

    def test_line_style_option_contract(self):
        """ Tests for LineStyleOption pseudo-type """
        putil.test.assert_exception(
            putil.plot.line_style_option,
            {'obj':5},
            ValueError,
            ('[START CONTRACT MSG: line_style_option]Argument '
             '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
        )
        putil.test.assert_exception(
            putil.plot.line_style_option,
            {'obj':'x'},
            ValueError,
            ("[START CONTRACT MSG: line_style_option]Argument "
             "`*[argument_name]*` is not one of ['-', '--', '-.', "
             "':'][STOP CONTRACT MSG]")
        )
        putil.plot.line_style_option(None)
        items = ['-', '--', '-.', ':']
        for item in items:
            putil.plot.line_style_option(item)

    def test_color_space_option_contract(self):
        """ Tests for LineStyleOption pseudo-type """
        putil.test.assert_exception(
            putil.plot.color_space_option,
            {'obj':5},
            ValueError,
            ('[START CONTRACT MSG: color_space_option]Argument '
             '`*[argument_name]*` is not valid[STOP CONTRACT MSG]')
        )
        putil.test.assert_exception(
            putil.plot.color_space_option,
            {'obj':'x'},
            ValueError,
            ("[START CONTRACT MSG: color_space_option]Argument "
             "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
             "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
             "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
             "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]")
        )
        items = [
            'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
            'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
            'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr',
            'YlOrRd'
        ]
        for item in items:
            putil.plot.color_space_option(item)

    def test_legend_position_validation(self):
        """ Tests _legend_position_validation() function behavior """
        items = [5, 'x']
        for item in items:
            assert putil.plot.panel._legend_position_validation(item)
        items = [
            None, 'BEST', 'UPPER RIGHT', 'UPPER LEFT', 'LOWER LEFT',
            'LOWER RIGHT', 'RIGHT', 'CENTER LEFT', 'CENTER RIGHT',
            'LOWER CENTER', 'UPPER CENTER', 'CENTER'
        ]
        for item in items:
            assert not putil.plot.panel._legend_position_validation(item)
