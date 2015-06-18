# figure.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,F0401,R0201,W0212,W0621

from __future__ import print_function
import matplotlib
import mock
import numpy
import os
import pytest
import sys

import putil.plot
from .fixtures import compare_images, IMGTOL
sys.path.append('..')
from tests.plot.gen_ref_images import unittest_figure_images


###
# Tests for Figure
###
class TestFigure(object):
    """ Tests for Figure """
    # pylint: disable=R0903,W0232
    def test_indep_var_label_wrong_type(self, default_panel):
        """ Test indep_var_label data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'indep_var_label':5},
            RuntimeError,
            'Argument `indep_var_label` is not valid'
        )
        # These assignments should not raise an exception
        putil.plot.Figure(panels=default_panel, indep_var_label=None)
        putil.plot.Figure(panels=default_panel, indep_var_label='sec')
        obj = putil.plot.Figure(panels=default_panel, indep_var_label='test')
        assert obj.indep_var_label == 'test'

    def test_indep_var_units_wrong_type(self, default_panel):
        """ Test indep_var_units data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'indep_var_units':5},
            RuntimeError,
            'Argument `indep_var_units` is not valid'
        )
        # These assignments should not raise an exception
        putil.plot.Figure(panels=default_panel, indep_var_units=None)
        putil.plot.Figure(panels=default_panel, indep_var_units='sec')
        obj = putil.plot.Figure(panels=default_panel, indep_var_units='test')
        assert obj.indep_var_units == 'test'

    def test_title_wrong_type(self, default_panel):
        """ Test title data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'title':5},
            RuntimeError,
            'Argument `title` is not valid'
        )
        # These assignments should not raise an exception
        putil.plot.Figure(panels=default_panel, title=None)
        putil.plot.Figure(panels=default_panel, title='sec')
        obj = putil.plot.Figure(panels=default_panel, title='test')
        assert obj.title == 'test'

    def test_log_indep_axis_wrong_type(self, default_panel):
        """ Test log_indep_axis data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'log_indep_axis':5},
            RuntimeError,
            'Argument `log_indep_axis` is not valid'
        )
        negative_data_source = putil.plot.BasicSource(
            indep_var=numpy.array([-5, 6, 7, 8]),
            dep_var=numpy.array([0.1, 10, 5, 4])
        )
        negative_series = putil.plot.Series(
            data_source=negative_data_source,
            label='negative data series'
        )
        negative_panel = putil.plot.Panel(series=negative_series)
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':negative_panel, 'log_indep_axis':True},
            ValueError,
            'Figure cannot cannot be plotted with a logarithmic independent '
            'axis because panel 0, series 0 contains negative independent '
            'data points'
        )
        # These assignments should not raise an exception
        obj = putil.plot.Figure(panels=default_panel, log_indep_axis=False)
        assert not obj.log_indep_axis
        obj = putil.plot.Figure(panels=default_panel, log_indep_axis=True)
        assert obj.log_indep_axis
        obj = putil.plot.Figure(panels=default_panel)
        assert not obj.log_indep_axis

    def test_fig_width_wrong_type(self, default_panel):
        """ Test figure width data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'fig_width':'a'},
            RuntimeError,
            'Argument `fig_width` is not valid'
        )
        # These assignments should not raise an exception
        obj = putil.plot.Figure(panels=None)
        assert obj.fig_width == None
        obj = putil.plot.Figure(panels=default_panel)
        assert (obj.fig_width-5.6 < 1e-10) or (obj.fig_width-5.61 < 1e-10)
        obj.fig_width = 5
        assert obj.fig_width == 5

    def test_fig_height_wrong_type(self, default_panel):
        """ Test figure height data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'fig_height':'a'},
            RuntimeError,
            'Argument `fig_height` is not valid'
        )
        # These assignments should not raise an exception
        obj = putil.plot.Figure(panels=None)
        assert obj.fig_height == None
        obj = putil.plot.Figure(panels=default_panel)
        assert obj.fig_height-4.31 < 1e-10
        obj.fig_height = 5
        assert obj.fig_height == 5

    def test_panels_wrong_type(self, default_panel):
        """ Test panel data validation """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':5},
            RuntimeError,
            'Argument `panels` is not valid'
        )
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':[default_panel, putil.plot.Panel(series=None)]},
            TypeError,
            'Panel 1 is not fully specified'
        )
        # These assignments should not raise an exception
        putil.plot.Figure(panels=None)
        putil.plot.Figure(panels=default_panel)

    def test_fig_wrong_type(self, default_panel):
        """ Test fig attribute """
        obj = putil.plot.Figure(panels=None)
        assert obj.fig == None
        obj = putil.plot.Figure(panels=default_panel)
        assert isinstance(obj.fig, matplotlib.figure.Figure)

    def test_indep_axis_scale(self, default_panel):
        """ Test indep_axis_scale property """
        obj = putil.plot.Figure(panels=None)
        assert obj.indep_axis_scale == None
        obj = putil.plot.Figure(panels=default_panel)
        assert obj.indep_axis_scale == 1

    def test_axes_list(self, default_panel):
        """ Test axes_list attribute """
        obj = putil.plot.Figure(panels=None)
        assert obj.axes_list == list()
        obj = putil.plot.Figure(panels=default_panel)
        comp_list = list()
        for num, axis_dict in enumerate(obj.axes_list):
            if ((axis_dict['number'] == num) and
               ((axis_dict['primary'] is None) or
               (isinstance(axis_dict['primary'], matplotlib.axes.Axes))) and
               ((axis_dict['secondary'] is None) or
               (isinstance(axis_dict['secondary'], matplotlib.axes.Axes)))):
                comp_list.append(True)
        assert comp_list == len(obj.axes_list)*[True]

    def test_specified_figure_size_too_small(self, default_panel):
        """
        Test that method behaves correctly when requested figure size is
        too small
        """
        # Continuous integration image is 5.61in wide
        putil.test.assert_exception(
            putil.plot.Figure,
            {
                'panels':default_panel,
                'indep_var_label':'Input',
                'indep_var_units':'Amps',
                'title':'My graph',
                'fig_width':0.1,
                'fig_height':200
            },
            RuntimeError,
            'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66'
        )
        putil.test.assert_exception(
            putil.plot.Figure,
            {
                'panels':default_panel,
                'indep_var_label':'Input',
                'indep_var_units':'Amps',
                'title':'My graph',
                'fig_width':200,
                'fig_height':0.1
            },
            RuntimeError,
            'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66'
        )
        putil.test.assert_exception(
            putil.plot.Figure,
            {
                'panels':default_panel,
                'indep_var_label':'Input',
                'indep_var_units':'Amps',
                'title':'My graph',
                'fig_width':0.1,
                'fig_height':0.1
            },
            RuntimeError,
            'Figure size is too small: minimum width = 5.6[1]*, minimum height 2.66'
        )

    def test_complete(self, default_panel):
        """ Test that _complete property behaves correctly """
        obj = putil.plot.Figure(panels=None)
        assert not obj._complete
        obj.panels = default_panel
        assert obj._complete
        obj = putil.plot.Figure(panels=None)
        putil.test.assert_exception(
            obj.show,
            {},
            RuntimeError,
            'Figure object is not fully specified'
        )

    def test_str(self, default_panel):
        """ Test that str behaves correctly """
        obj = putil.plot.Figure(panels=None)
        ret = (
            'Panels: None\n'
            'Independent variable label: not specified\n'
            'Independent variable units: not specified\n'
            'Logarithmic independent axis: False\n'
            'Title: not specified\n'
            'Figure width: None\n'
            'Figure height: None\n'
        )
        assert str(obj) == ret
        obj = putil.plot.Figure(
            panels=default_panel,
            indep_var_label='Input',
            indep_var_units='Amps',
            title='My graph'
        )
        ret = (
            'Panel 0:\n'
            '   Series 0:\n'
            '      Independent variable: [ 5.0, 6.0, 7.0, 8.0 ]\n'
            '      Dependent variable: [ 0.0, -10.0, 5.0, 4.0 ]\n'
            '      Label: test series\n'
            '      Color: k\n'
            '      Marker: o\n'
            '      Interpolation: CUBIC\n'
            '      Line style: -\n'
            '      Secondary axis: False\n'
            '   Primary axis label: Primary axis\n'
            '   Primary axis units: A\n'
            '   Secondary axis label: Secondary axis\n'
            '   Secondary axis units: B\n'
            '   Logarithmic dependent axis: False\n'
            '   Display independent axis: False\n'
            '   Legend properties:\n'
            '      cols: 1\n'
            '      pos: BEST\n'
            'Independent variable label: Input\n'
            'Independent variable units: Amps\n'
            'Logarithmic independent axis: False\n'
            'Title: My graph\n'
        )
        ret_ci = ret + 'Figure width: 5.61\n'
        ret += 'Figure width: 5.6\n'
        ret_ci += 'Figure height: 2.66\n'
        ret += 'Figure height: 2.66\n'

        assert (str(obj) == ret) or (str(obj) == ret_ci)

    def test_cannot_delete_attributes(self, default_panel):
        """ Test that del method raises an exception on all class attributes """
        obj = putil.plot.Figure(panels=default_panel)
        with pytest.raises(AttributeError) as excinfo:
            del obj.panels
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_var_label
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_var_units
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.title
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.log_indep_axis
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig_width
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig_height
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.axes_list
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_axis_scale
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"

    def test_show(self, default_panel, capsys):
        """ Test that show() method behaves correctly """
        def mock_show():
            print('show called')
        obj = putil.plot.Figure(panels=default_panel)
        with mock.patch('putil.plot.figure.plt.show', side_effect=mock_show):
            obj.show()
        out, _ = capsys.readouterr()
        assert out == 'show called\n'

    def test_iterator(self, default_panel):
        """ Test that __iter__() method behaves correctly """
        ds1_obj = putil.plot.BasicSource(
            indep_var=numpy.array([100, 200, 300, 400]),
            dep_var=numpy.array([1, 2, 3, 4])
        )
        series1_obj = putil.plot.Series(
            data_source=ds1_obj,
            label='series 1',
            interp=None
        )
        panel2 = putil.plot.Panel(series=series1_obj)
        obj = putil.plot.Figure(panels=[default_panel, panel2])
        for num, panel in enumerate(obj):
            if num == 0:
                assert panel == default_panel
            if num == 1:
                assert panel == panel2

    def test_images(self, tmpdir):
        """ Compare images to verify correct plotting of figure """
        tmpdir.mkdir('test_images')
        images_dict_list = unittest_figure_images(mode='test', test_dir=str(tmpdir))
        for images_dict in images_dict_list:
            ref_file_name = images_dict['ref_file_name']
            ref_ci_file_name = images_dict['ref_ci_file_name']
            test_file_name = images_dict['test_file_name']
            metrics = compare_images(ref_file_name, test_file_name)
            result = (metrics[0] < IMGTOL) and (metrics[1] < IMGTOL)
            metrics_ci = compare_images(ref_ci_file_name, test_file_name)
            result_ci = (metrics_ci[0] < IMGTOL) and (metrics_ci[1] < IMGTOL)
            if (not result) and (not result_ci):
                print('Images do not match')
                print('Reference image: file://{0}'.format(
                    os.path.realpath(ref_file_name)
                ))
                print('Reference CI image: file://{0}'.format(
                    os.path.realpath(ref_ci_file_name)
                ))
                print('Actual image: file://{0}'.format(
                    os.path.realpath(test_file_name)
                ))
            #print 'Comparison: {0} with {1} -> {2} {3}'.format(
            #   ref_file_name,
            #   test_file_name,
            #   result,
            #   metrics
            #)
            assert result or result_ci

    def test_nonzero(self, default_panel):
        """ Test __nonzero__() function """
        obj = putil.plot.Figure()
        assert not obj
        obj = putil.plot.Figure(
            panels=default_panel
        )
        assert obj
        obj = putil.plot.Figure(
            panels=2*[default_panel]
        )
        assert obj
