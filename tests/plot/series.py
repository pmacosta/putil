# series.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,F0401,R0201,R0204,R0903,W0201,W0212,W0232,W0621

# Standard library imports
from __future__ import print_function
import sys
# PyPI imports
import numpy
import pytest
import matplotlib
# Putil imports
from putil.test import AE, AI, AROPROP, RE, compare_strings
import putil.plot
from .fixtures import compare_image_set
sys.path.append('..')
from tests.plot.gen_ref_images import unittest_series_images


###
# Global variables
###
FOBJ = putil.plot.Series


###
# Test classes
###
class TestSeries(object):
    """ Tests for Series class """
    ### Private methods
    @pytest.mark.parametrize(
        'mdict', [
            {'value':None, 'string':'None'},
            {'value':'o', 'string':'o'},
            {
                'value':matplotlib.path.Path([(0, 0), (1, 1)]),
                'string':'matplotlib.path.Path object'
            },
            {'value':[(0, 0), (1, 1)], 'string':'[(0, 0), (1, 1)]'},
            {'value':r'$a_{b}$', 'string':r'$a_{b}$'},
            {
                'value':matplotlib.markers.TICKLEFT,
                'string':'matplotlib.markers.TICKLEFT'
            }
        ]
    )
    def test_str(self, default_source, mdict):
        """ Test __str__ method behavior """
        obj = putil.plot.Series(
            data_source=default_source, label='test', marker=mdict['value']
        )
        ret = (
            'Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
            'Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
            'Label: test\n'
            'Color: k\n'
            'Marker: {0}\n'
            'Interpolation: CUBIC\n'
            'Line style: -\n'
            'Secondary axis: False'.format(mdict['string'])
        )
        compare_strings(str(obj), ret)

    ### Properties
    @pytest.mark.parametrize(
        'color', [
            None,
            'moccasin',
            0.5,
            '#ABCDEF',
            (0.5, 0.5, 0.5),
            [0.25, 0.25, 0.25, 0.25]
        ]
    )
    def test_color(self, default_source, color):
        """ Test color property behavior """
        proc_color = lambda x: x.lower() if isinstance(x, str) else x
        putil.plot.Series(data_source=default_source, label='test', color=None)
        obj = putil.plot.Series(
            data_source=default_source, label='test', color=color
        )
        assert obj.color == proc_color(color)

    @pytest.mark.series
    @pytest.mark.parametrize(
        'color', [
            'invalid_color_name',
            -0.01,
            1.1,
            '#ABCDEX',
            (-1, 1, 1),
            [1, 2, 0.5],
            [1, 1, 2],
            (-1, 1, 1, 1),
            [1, 2, 0.5, 0.5],
            [1, 1, 2, 1],
            (1, 1, 1, -1)
        ]
    )
    def test_color_exceptions(self, default_source, color):
        """ Test color property exceptions """
        AI(FOBJ, 'color', default_source, 'test', color=default_source)
        exmsg = 'Invalid color specification'
        AE(FOBJ, TypeError, exmsg, default_source, 'test', color)

    def test_data_source(self, default_source):
        """ Test data source property exception """
        class TestSource(object):
            def __init__(self):
                pass
        obj = TestSource()
        obj.indep_var = numpy.array([5, 6, 7, 8])
        obj.dep_var = numpy.array([0, -10, 5, 4])
        putil.plot.Series(data_source=None, label='test')
        putil.plot.Series(data_source=obj, label='test')
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert (obj.indep_var == numpy.array([5, 6, 7, 8])).all()
        assert (obj.dep_var == numpy.array([0, -10, 5, 4])).all()

    @pytest.mark.series
    def test_data_source_exceptions(self):
        """ Test data_source property exceptions """
        class TestSource(object):
            def __init__(self):
                pass
        obj = putil.plot.BasicSource(
            indep_var=numpy.array([1, 2, 3, 4]),
            dep_var=numpy.array([10, 20, 30, 40])
        )
        obj._indep_var = None
        exmsg = 'Argument `data_source` is not fully specified'
        AE(FOBJ, RE, exmsg, obj, 'test')
        exmsg = 'Argument `data_source` does not have an `indep_var` attribute'
        AE(FOBJ, RE, exmsg, 5, 'test')
        obj = TestSource()
        obj.indep_var = numpy.array([5, 6, 7, 8])
        exmsg = 'Argument `data_source` does not have an `dep_var` attribute'
        AE(FOBJ, RE, exmsg, obj, 'test')

    def test_interp(self, default_source):
        """ Test interp property behavior """
        source_obj = putil.plot.BasicSource(
            indep_var=numpy.array([5]), dep_var=numpy.array([0])
        )
        items = [
            (None, default_source),
            ('STRAIGHT', source_obj),
            ('STEP', source_obj),
            ('LINREG', source_obj)
        ]
        for interp, source in items:
            putil.plot.Series(data_source=source, label='test', interp=interp)
        items = ['straight', 'StEp', 'CUBIC', 'linreg']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source, label='test', interp=item
            )
            assert obj.interp == item.upper()
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.interp == 'CUBIC'

    @pytest.mark.series
    def test_interp_exceptions(self, default_source):
        """ Test interp property exceptions """
        AI(FOBJ, 'interp', default_source, 'test', interp=5)
        exmsg = (
            "Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
            "'LINREG'] (case insensitive)"
        )
        AE(FOBJ, ValueError, exmsg, default_source, 'test', interp='NO_OPTION')
        source_obj = putil.plot.BasicSource(
            indep_var=numpy.array([5]), dep_var=numpy.array([0])
        )
        exmsg = 'At least 4 data points are needed for CUBIC interpolation'
        AE(FOBJ, ValueError, exmsg, source_obj, 'test', interp='CUBIC')

    def test_label(self, default_source):
        """ Test label property behavior """
        putil.plot.Series(data_source=default_source, label=None)
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.label == 'test'

    @pytest.mark.series
    def test_label_exceptions(self, default_source):
        """ Test label property exceptions """
        AI(FOBJ, 'label', default_source, 5)

    def test_line_style(self, default_source):
        """ Test line_style property behavior """
        putil.plot.Series(
            data_source=default_source, label='test', line_style=None
        )
        items = ['-', '--', '-.', ':']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source, label='test', line_style=item
            )
            assert obj.line_style == item
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.line_style == '-'

    @pytest.mark.series
    def test_line_style_exceptions(self, default_source):
        """ Test line_style property exceptions """
        AI(FOBJ, 'line_style', default_source, 'test', line_style=5)
        exmsg = "Argument `line_style` is not one of ['-', '--', '-.', ':']"
        AE(FOBJ, ValueError, exmsg, default_source, 'test', line_style='x')

    def test_marker(self, default_source):
        """ Test marker property behavior """
        obj = putil.plot.Series(
            data_source=default_source, label='test', marker=None
        )
        assert obj.marker is None
        obj = putil.plot.Series(
            data_source=default_source, label='test', marker='D'
        )
        assert obj.marker == 'D'
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.marker == 'o'

    @pytest.mark.series
    def test_marker_exceptions(self, default_source):
        """ Test marker property exceptions  """
        AI(FOBJ, 'marker', default_source, 'test', marker='hello')

    def test_secondary_axis(self, default_source):
        """ Test secondary_axis property behavior """
        putil.plot.Series(
            data_source=default_source, label='test', secondary_axis=None
        )
        items = [False, True]
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source, label='test', secondary_axis=item
            )
            assert obj.secondary_axis == item
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert not obj.secondary_axis

    @pytest.mark.series
    def test_secondary_axis_exceptions(self, default_source):
        """ Test secondary_axis property exceptions """
        AI(FOBJ, 'secondary_axis', default_source, 'test', secondary_axis=5)

    ### Miscellaneous
    def test_calculate_curve(self, default_source):
        """ Test that interpolated curve is calculated when appropriate """
        items = [None, 'STRAIGHT', 'STEP']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source, label='test', interp=item
            )
            assert (obj.interp_indep_var, obj.interp_dep_var) == (None, None)
        items = ['CUBIC', 'LINREG']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source, label='test', interp=item
            )
            assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)

    def test_scale_indep_var(self, default_source):
        """ Test that independent variable scaling works """
        obj = putil.plot.Series(
            data_source=default_source, label='test', interp=None
        )
        assert obj.scaled_indep_var is not None
        assert obj.scaled_dep_var is not None
        assert obj.scaled_interp_indep_var is None
        assert obj.scaled_interp_dep_var is None
        obj._scale_indep_var(2)
        obj._scale_dep_var(4)
        indep_var = numpy.array([2.5, 3.0, 3.5, 4.0])
        dep_var = numpy.array([0.0, -2.5, 1.25, 1.0])
        assert (obj.scaled_indep_var == indep_var).all()
        assert (obj.scaled_dep_var == dep_var).all()
        assert obj.scaled_interp_indep_var is None
        assert obj.scaled_interp_dep_var is None
        obj.interp = 'CUBIC'
        assert (obj.scaled_indep_var == indep_var).all()
        assert (obj.scaled_dep_var == dep_var).all()
        assert obj.scaled_interp_indep_var is not None
        assert obj.scaled_interp_dep_var is not None

    @pytest.mark.series
    def test_cannot_delete_attributes_exceptions(self, default_source):
        """
        Test that del method raises an exception on all class attributes
        """
        obj = putil.plot.Series(data_source=default_source, label='test')
        props = [
            'data_source',
            'label',
            'color',
            'marker',
            'interp',
            'line_style',
            'secondary_axis'
        ]
        for prop in props:
            AROPROP(obj, prop)

    def test_images(self, tmpdir):
        """ Compare images to verify correct plotting of series """
        tmpdir.mkdir('test_images')
        images_dict_list = unittest_series_images(
            mode='test', test_dir=str(tmpdir)
        )
        assert compare_image_set(tmpdir, images_dict_list, 'series')
