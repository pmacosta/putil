# ccontracts.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0201,W0108,W0212,W0232,W0613

# PyPI imports
import numpy
import pytest
# Putil imports
import putil.plot
from putil.test import AE


###
# Global variables
###
emsg = lambda msg: (
    '[START CONTRACT MSG: {0}]Argument `*[argument_name]*` '
    'is not valid[STOP CONTRACT MSG]'.format(msg)
)

###
# Test classes
###
class TestContracts(object):
    """ Test for ccontract sub-module """
    def test_real_num_contract(self):
        """ Tests for RealNumber pseudo-type """
        obj = putil.plot.real_num
        items = ['a', [1, 2, 3], False]
        for item in items:
            AE(obj, ValueError, emsg('real_num'), obj=item)
        items = [-1, 1, 2.0]
        for item in items:
            putil.plot.real_num(item)

    def test_positive_real_num_contract(self):
        """ Tests for PositiveRealNumber pseudo-type """
        obj = putil.plot.positive_real_num
        items = ['a', [1, 2, 3], False, -1, -2.0]
        for item in items:
            AE(obj, ValueError, emsg('positive_real_num'), obj=item)
        items = [1, 2.0]
        for item in items:
            putil.plot.positive_real_num(item)

    def test_offset_range_contract(self):
        """ Tests for PositiveRealNumber pseudo-type """
        obj = putil.plot.offset_range
        items = ['a', [1, 2, 3], False, -0.1, -1.1]
        for item in items:
            AE(obj, ValueError, emsg('offset_range'), obj=item)
        items = [0, 0.5, 1]
        for item in items:
            putil.plot.offset_range(item)

    def test_function_contract(self):
        """ Tests for Function pseudo-type """
        def func1():
            pass
        AE(putil.plot.function, ValueError, emsg('function'), obj='a')
        items = [None, func1]
        for item in items:
            putil.plot.function(item)

    def test_real_numpy_vector_contract(self):
        """ Tests for RealNumpyVector pseudo-type """
        obj = putil.plot.real_numpy_vector
        items = [
            'a',
            [1, 2, 3],
            numpy.array([]),
            numpy.array([[1, 2, 3], [4, 5, 6]]),
            numpy.array(['a', 'b'])
        ]
        for item in items:
            AE(obj, ValueError, emsg('real_numpy_vector'), obj=item)
        items = [
            numpy.array([1, 2, 3]),
            numpy.array([10.0, 8.0, 2.0]),
            numpy.array([10.0])
        ]
        for item in items:
            putil.plot.real_numpy_vector(item)

    def test_increasing_real_numpy_vector_contract(self):
        """ Tests for IncreasingRealNumpyVector pseudo-type """
        obj = putil.plot.increasing_real_numpy_vector
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
            AE(obj, ValueError, emsg('increasing_real_numpy_vector'), obj=item)
        items = [
            numpy.array([1, 2, 3]),
            numpy.array([10.0, 12.1, 12.5]),
            numpy.array([10.0])
        ]
        for item in items:
            putil.plot.increasing_real_numpy_vector(item)

    @pytest.mark.parametrize('option', ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG'])
    def test_interpolation_option_contract(self, option):
        """ Tests for InterpolationOption pseudo-type """
        obj = putil.plot.interpolation_option
        AE(obj, ValueError, emsg('interpolation_option'), obj=5)
        msg = (
            "[START CONTRACT MSG: interpolation_option]Argument "
            "`*[argument_name]*` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
            "'LINREG'] (case insensitive)[STOP CONTRACT MSG]"
        )
        AE(obj, ValueError, msg, obj='x')
        putil.plot.interpolation_option(None)
        putil.plot.interpolation_option(option)
        putil.plot.interpolation_option(option.lower())

    @pytest.mark.parametrize('option', ['-', '--', '-.', ':'])
    def test_line_style_option_contract(self, option):
        """ Tests for LineStyleOption pseudo-type """
        obj = putil.plot.line_style_option
        AE(obj, ValueError, emsg('line_style_option'), obj=5)
        msg = (
            "[START CONTRACT MSG: line_style_option]Argument "
            "`*[argument_name]*` is not one of ['-', '--', '-.', "
            "':'][STOP CONTRACT MSG]"
        )
        AE(obj, ValueError, msg, obj='x')
        putil.plot.line_style_option(None)
        putil.plot.line_style_option(option)

    @pytest.mark.parametrize(
        'option', [
            'binary', 'Blues', 'BuGn', 'BuPu', 'GnBu', 'Greens',
            'Greys', 'Oranges', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd',
            'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', 'YlOrBr',
            'YlOrRd'
        ]
    )
    def test_color_space_option_contract(self, option):
        """ Tests for LineStyleOption pseudo-type """
        obj = putil.plot.color_space_option
        AE(obj, ValueError, emsg('color_space_option'), obj=5)
        msg = (
            "[START CONTRACT MSG: color_space_option]Argument "
            "`*[argument_name]*` is not one of 'binary', 'Blues', 'BuGn', "
            "'BuPu', 'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd', 'PuBu', "
            "'PuBuGn', 'PuRd', 'Purples', 'RdPu', 'Reds', 'YlGn', 'YlGnBu', "
            "'YlOrBr' or 'YlOrRd' (case insensitive)[STOP CONTRACT MSG]"
        )
        AE(obj, ValueError, msg, obj='x')
        putil.plot.color_space_option(option)

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
