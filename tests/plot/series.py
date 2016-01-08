# series.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,F0401,R0201,R0204,R0903,W0201,W0212,W0232,W0621

# Standard library imports
from __future__ import print_function
import os
import sys
# PyPI imports
import matplotlib
import numpy
import pytest
# Putil imports
import putil.plot
from .fixtures import compare_images, export_image, IMGTOL
sys.path.append('..')
from tests.plot.gen_ref_images import unittest_series_images


###
# Test classes
###
class TestSeries(object):
    """ Tests for Series class """
    ### Private methods
    def test_str(self, default_source):
        """ Test __str__ method behavior """
        marker_list = [
            {
                'value':None,
                'string':'None'
            },
            {
                'value':'o',
                'string':'o'
            },
            {
                'value':matplotlib.path.Path([(0, 0), (1, 1)]),
                'string':'matplotlib.path.Path object'
            },
            {
                'value':[(0, 0), (1, 1)],
                'string':'[(0, 0), (1, 1)]'
            },
            {
                'value':r'$a_{b}$',
                'string':r'$a_{b}$'
            },
            {
                'value':matplotlib.markers.TICKLEFT,
                'string':'matplotlib.markers.TICKLEFT'
            }
        ]
        for marker_dict in marker_list:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                marker=marker_dict['value']
            )
            ret = (
                'Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
                'Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
                'Label: test\n'
                'Color: k\n'
                'Marker: {0}\n'
                'Interpolation: CUBIC\n'
                'Line style: -\n'
                'Secondary axis: False'.format(marker_dict['string'])
            )
            if str(obj) != ret:
                print('Object:')
                print(str(obj))
                print('')
                print('Comparison:')
                print(ret)
            assert str(obj) == ret

    ### Properties
    def test_color(self, default_source):
        """ Test color property behavior """
        items = [
            None,
            'moccasin',
            0.5,
            '#ABCDEF',
            (0.5, 0.5, 0.5),
            [0.25, 0.25, 0.25, 0.25]
        ]
        putil.plot.Series(data_source=default_source, label='test', color=None)
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                color=item
            )
            assert (
                obj.color
                ==
                (item.lower() if isinstance(item, str) else item)
            )

    @pytest.mark.series
    def test_color_exceptions(self, default_source):
        """ Test color property exceptions """
        putil.test.assert_exception(
            putil.plot.Series,
            {
                'data_source':default_source,
                'label':'test',
                'color':default_source
            },
            RuntimeError,
            'Argument `color` is not valid'
        )
        items = [
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
        for item in items:
            putil.test.assert_exception(
                putil.plot.Series,
                {'data_source':default_source, 'label':'test', 'color':item},
                TypeError,
                'Invalid color specification'
            )

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
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':obj, 'label':'test'},
            RuntimeError,
            'Argument `data_source` is not fully specified'
        )
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':5, 'label':'test'},
            RuntimeError,
            'Argument `data_source` does not have an `indep_var` attribute'
        )
        obj = TestSource()
        obj.indep_var = numpy.array([5, 6, 7, 8])
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':obj, 'label':'test'},
            RuntimeError,
            'Argument `data_source` does not have an `dep_var` attribute'
        )

    def test_interp(self, default_source):
        """ Test interp property behavior """
        source_obj = putil.plot.BasicSource(
            indep_var=numpy.array([5]),
            dep_var=numpy.array([0])
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
                data_source=default_source,
                label='test',
                interp=item
            )
            assert obj.interp == item.upper()
        obj = putil.plot.Series(
            data_source=default_source,
            label='test'
        )
        assert obj.interp == 'CUBIC'

    @pytest.mark.series
    def test_interp_exceptions(self, default_source):
        """ Test interp property exceptions """
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':'test', 'interp':5},
            RuntimeError,
            'Argument `interp` is not valid'
        )
        putil.test.assert_exception(
            putil.plot.Series,
            {
                'data_source':default_source,
                'label':'test',
                'interp':'NOT_AN_OPTION'
            },
            ValueError,
            "Argument `interp` is not one of ['STRAIGHT', 'STEP', 'CUBIC', "
            "'LINREG'] (case insensitive)"
        )
        source_obj = putil.plot.BasicSource(
            indep_var=numpy.array([5]),
            dep_var=numpy.array([0])
        )
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':source_obj, 'label':'test', 'interp':'CUBIC'},
            ValueError,
            'At least 4 data points are needed for CUBIC interpolation'
        )

    def test_label(self, default_source):
        """ Test label property behavior """
        putil.plot.Series(data_source=default_source, label=None)
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.label == 'test'

    @pytest.mark.series
    def test_label_exceptions(self, default_source):
        """ Test label property exceptions """
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':5},
            RuntimeError,
            'Argument `label` is not valid'
        )

    def test_line_style(self, default_source):
        """ Test line_style property behavior """
        putil.plot.Series(
            data_source=default_source, label='test', line_style=None
        )
        items = ['-', '--', '-.', ':']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                line_style=item
            )
            assert obj.line_style == item
        obj = putil.plot.Series(
            data_source=default_source,
            label='test'
        )
        assert obj.line_style == '-'

    @pytest.mark.series
    def test_line_style_exceptions(self, default_source):
        """ Test line_style property exceptions """
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':'test', 'line_style':5},
            RuntimeError,
            'Argument `line_style` is not valid'
        )
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':'test', 'line_style':'x'},
            ValueError,
            "Argument `line_style` is not one of ['-', '--', '-.', ':']"
        )

    def test_marker(self, default_source):
        """ Test marker property behavior """
        obj = putil.plot.Series(
            data_source=default_source,
            label='test',
            marker=None
        )
        assert obj.marker is None
        obj = putil.plot.Series(
            data_source=default_source,
            label='test',
            marker='D'
        )
        assert obj.marker == 'D'
        obj = putil.plot.Series(data_source=default_source, label='test')
        assert obj.marker == 'o'

    @pytest.mark.series
    def test_marker_exceptions(self, default_source):
        """ Test marker property exceptions  """
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':'test', 'marker':'hello'},
            RuntimeError,
            'Argument `marker` is not valid'
        )

    def test_secondary_axis(self, default_source):
        """ Test secondary_axis property behavior """
        putil.plot.Series(
            data_source=default_source,
            label='test',
            secondary_axis=None
        )
        items = [False, True]
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                secondary_axis=item
            )
            assert obj.secondary_axis == item
        obj = putil.plot.Series(
            data_source=default_source,
            label='test'
        )
        assert not obj.secondary_axis

    @pytest.mark.series
    def test_secondary_axis_exceptions(self, default_source):
        """ Test secondary_axis property exceptions """
        putil.test.assert_exception(
            putil.plot.Series,
            {'data_source':default_source, 'label':'test', 'secondary_axis':5},
            RuntimeError,
            'Argument `secondary_axis` is not valid'
        )

    ### Miscellaneous
    def test_calculate_curve(self, default_source):
        """ Test that interpolated curve is calculated when appropriate """
        items = [None, 'STRAIGHT', 'STEP']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                interp=item
            )
            assert (obj.interp_indep_var, obj.interp_dep_var) == (None, None)
        items = ['CUBIC', 'LINREG']
        for item in items:
            obj = putil.plot.Series(
                data_source=default_source,
                label='test',
                interp=item
            )
            assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)
        obj = putil.plot.Series(
            data_source=default_source,
            label='test'
        )
        assert (obj.interp_indep_var, obj.interp_dep_var) != (None, None)

    def test_scale_indep_var(self, default_source):
        """ Test that independent variable scaling works """
        obj = putil.plot.Series(
            data_source=default_source,
            label='test',
            interp=None
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
        with pytest.raises(AttributeError) as excinfo:
            del obj.data_source
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.label
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.color
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.marker
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.interp
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.line_style
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.secondary_axis
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"

    def test_images(self, tmpdir):
        """ Compare images to verify correct plotting of series """
        tmpdir.mkdir('test_images')
        images_dict_list = unittest_series_images(
            mode='test', test_dir=str(tmpdir)
        )
        global_result = True
        for images_dict in images_dict_list:
            ref_file_name_list = images_dict['ref_fname']
            test_file_name = images_dict['test_fname']
            print('Reference images:')
            for ref_file_name in ref_file_name_list:
                print('   file://{0}'.format(
                        os.path.realpath(ref_file_name)
                    )
                )
            print('Actual image:')
            print('   file://{0}'.format(
                    os.path.realpath(test_file_name)
                )
            )
            for ref_file_name in ref_file_name_list:
                metrics = compare_images(ref_file_name, test_file_name)
                result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
                if result:
                    break
            else:
                print('Images do not match')
                global_result = False
                export_image(test_file_name)
            print('')
        assert global_result
