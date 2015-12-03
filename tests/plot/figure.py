# figure.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,E1129,F0401,R0201,W0212,W0621

# Standard library imports
from __future__ import print_function
import os
import re
import sys
if sys.hexversion >= 0x03000000:
    import unittest.mock as mock
# PyPI imports
import matplotlib
import numpy
import pytest
if sys.hexversion < 0x03000000:
    import mock
# Putil imports
import putil.misc
import putil.plot
from .fixtures import compare_images, IMGTOL
sys.path.append('..')
from tests.plot.gen_ref_images import unittest_figure_images


###
# Test classes
###
class TestFigure(object):
    """ Tests for Figure class """
    # pylint: disable=R0903,R0904,W0232
    ### Private methods
    def test_complete(self, default_panel):
        """ Test _complete property behavior """
        obj = putil.plot.Figure(panels=None)
        assert not obj._complete
        obj.panels = default_panel
        assert obj._complete

    @pytest.mark.figure
    def test_complete_exceptions(self):
        """ Test _complete property exceptions """
        obj = putil.plot.Figure(panels=None)
        putil.test.assert_exception(
            obj.show,
            {},
            RuntimeError,
            'Figure object is not fully specified'
        )

    def test_iter(self, default_panel):
        """ Test __iter__ method behavior """
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

    def test_nonzero(self, default_panel):
        """ Test __nonzero__ method behavior """
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

    def test_str(self, default_panel):
        """ Test __str__ method behavior """
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
        ref = (
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
            'Figure width: (5\\.6|6\\.2).*\n'
            'Figure height: 2.6.*\n'
        )
        actual = str(obj)
        ref_invariant = '\n'.join(ref.split('\n')[:-3])
        actual_invariant = '\n'.join(actual.split('\n')[:-3])
        assert ref_invariant == actual_invariant
        regexp = re.compile('\n'.join(ref.split('\n')[-3:]))
        assert regexp.match('\n'.join(actual.split('\n')[-3:]))

    ### Public methods
    def test_save(self, default_panel):
        """ Test save method behavior """
        obj = putil.plot.Figure(
            panels=default_panel
        )
        with putil.misc.TmpFile() as fname:
            obj.save(fname=fname, ftype='PNG')
        with putil.misc.TmpFile() as fname:
            obj.save(fname=fname, ftype='EPS')
        # Test extension handling
        # No exception
        fname = os.path.join(os.path.dirname(__file__), 'test_file1')
        obj.save(fname, ftype='PNG')
        fref = '{fname}.png'.format(fname=fname)
        assert os.path.exists(fref)
        with putil.misc.ignored(OSError):
            os.remove(fref)
        # No exception but trailing period
        fname = os.path.join(os.path.dirname(__file__), 'test_file2.')
        obj.save(fname, ftype='EPS')
        fref = '{fname}.eps'.format(
            fname=os.path.join(os.path.dirname(__file__), 'test_file2')
        )
        assert os.path.exists(fref)
        with putil.misc.ignored(OSError):
            os.remove(fref)
        # Extension given, overrides file format
        fname = os.path.join(os.path.dirname(__file__), 'test_file3.ext')
        obj.save(fname, ftype='EPS')
        fref = fname
        assert os.path.exists(fref)
        with putil.misc.ignored(OSError):
            os.remove(fref)

    @pytest.mark.figure
    def test_save_exceptions(self, default_panel):
        """ Test save method exceptions """
        obj = putil.plot.Figure(
            panels=default_panel
        )
        putil.test.assert_exception(
            obj.save,
            {'fname':3},
            RuntimeError,
            'Argument `fname` is not valid'
        )
        putil.test.assert_exception(
            obj.save,
            {'fname':'test\0'},
            RuntimeError,
            'Argument `fname` is not valid'
        )
        putil.test.assert_exception(
            obj.save,
            {'fname':'myfile', 'ftype':5},
            RuntimeError,
            'Argument `ftype` is not valid'
        )
        putil.test.assert_exception(
            obj.save,
            {'fname':'myfile', 'ftype':'bmp'},
            RuntimeError,
            'Unsupported file type: bmp'
        )

    def test_show(self, default_panel, capsys):
        """ Test that show method behavior """
        def mock_show():
            print('show called')
        obj = putil.plot.Figure(panels=default_panel)
        with mock.patch('putil.plot.figure.plt.show', side_effect=mock_show):
            obj.show()
        out, _ = capsys.readouterr()
        assert out == 'show called\n'

    ### Properties
    def test_axes_list(self, default_panel):
        """ Test axes_list property behavior """
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

    def test_fig(self, default_panel):
        """ Test fig property behavior """
        obj = putil.plot.Figure(panels=None)
        assert obj.fig is None
        obj = putil.plot.Figure(panels=default_panel)
        assert isinstance(obj.fig, matplotlib.figure.Figure)

    def test_fig_width(self, default_panel):
        """ Test figure width attributes """
        obj = putil.plot.Figure(panels=None)
        assert obj.fig_width is None
        obj = putil.plot.Figure(panels=default_panel)
        assert (
            (obj.fig_width-5.6 < 1e-10) or
            (obj.fig_width-5.61 < 1e-10) or
            (obj.fig_width-6.2 < 1e-10)
        )
        obj.fig_width = 5
        assert obj.fig_width == 5

    @pytest.mark.figure
    def test_fig_width_exceptions(self, default_panel):
        """ Test figure width property exceptions """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'fig_width':'a'},
            RuntimeError,
            'Argument `fig_width` is not valid'
        )

    def test_fig_height(self, default_panel):
        """ Test figure height property behavior """
        obj = putil.plot.Figure(panels=None)
        assert obj.fig_height is None
        obj = putil.plot.Figure(panels=default_panel)
        assert obj.fig_height-4.31 < 1e-10
        obj.fig_height = 5
        assert obj.fig_height == 5

    @pytest.mark.figure
    def test_fig_height_exceptions(self, default_panel):
        """ Test figure height property exceptions """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'fig_height':'a'},
            RuntimeError,
            'Argument `fig_height` is not valid'
        )

    def test_indep_axis_scale(self, default_panel):
        """ Test indep_axis_scale property """
        obj = putil.plot.Figure(panels=None)
        assert obj.indep_axis_scale is None
        obj = putil.plot.Figure(panels=default_panel)
        assert obj.indep_axis_scale == 1

    def test_indep_axis_ticks(self, default_panel):
        """ Test indep_axis_ticks property behavior """
        obj = putil.plot.Figure(
            panels=default_panel,
            indep_axis_ticks=[
                1000, 2000, 3000, 3500
            ]
        )
        assert obj.indep_axis_ticks == [
            1.0, 2.0, 3.0, 3.5
        ]
        obj = putil.plot.Figure(
            panels=default_panel,
            indep_axis_ticks=numpy.array(
                [1E6, 2E6, 3E6, 3.5E6]
            )
        )
        assert obj.indep_axis_ticks == [
            1.0, 2.0, 3.0, 3.5
        ]
        # Logarithmic independent axis tick marks
        # cannot be overridden
        obj = putil.plot.Figure(
            panels=default_panel,
            log_indep_axis=True,
            indep_axis_ticks=numpy.array(
                [1E6, 2E6, 3E6, 3.5E6]
            )
        )
        assert obj.indep_axis_ticks == [
            1.0, 10.0
        ]

    @pytest.mark.figure
    def test_indep_axis_ticks_exceptions(self, default_panel):
        """ Test indep_axis_ticks exceptions """
        obj = putil.plot.Figure(panels=None)
        assert obj.indep_axis_ticks is None
        putil.test.assert_exception(
            putil.plot.Figure,
            {
                'panels':default_panel,
                'indep_axis_ticks':5
            },
            RuntimeError,
            'Argument `indep_axis_ticks` is not valid'
        )

    def test_indep_var_label(self, default_panel):
        """ Test indep_var_label property behavior """
        putil.plot.Figure(panels=default_panel, indep_var_label=None)
        putil.plot.Figure(panels=default_panel, indep_var_label='sec')
        obj = putil.plot.Figure(panels=default_panel, indep_var_label='test')
        assert obj.indep_var_label == 'test'

    @pytest.mark.figure
    def test_indep_var_label_exceptions(self, default_panel):
        """ Test indep_var_label property exceptions """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'indep_var_label':5},
            RuntimeError,
            'Argument `indep_var_label` is not valid'
        )

    def test_indep_var_units(self, default_panel):
        """ Test indep_var_units property behavior """
        putil.plot.Figure(panels=default_panel, indep_var_units=None)
        putil.plot.Figure(panels=default_panel, indep_var_units='sec')
        obj = putil.plot.Figure(panels=default_panel, indep_var_units='test')
        assert obj.indep_var_units == 'test'

    @pytest.mark.figure
    def test_indep_var_units_exceptions(self, default_panel):
        """ Test indep_var_units exceptions """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'indep_var_units':5},
            RuntimeError,
            'Argument `indep_var_units` is not valid'
        )

    def test_log_indep_axis(self, default_panel):
        """ Test log_indep_axis property behavior """
        obj = putil.plot.Figure(panels=default_panel, log_indep_axis=False)
        assert not obj.log_indep_axis
        obj = putil.plot.Figure(panels=default_panel, log_indep_axis=True)
        assert obj.log_indep_axis
        obj = putil.plot.Figure(panels=default_panel)
        assert not obj.log_indep_axis

    @pytest.mark.figure
    def test_log_indep_axis_exceptions(self, default_panel):
        """ Test log_indep_axis property exceptions """
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
            'Figure cannot be plotted with a logarithmic independent '
            'axis because panel 0, series 0 contains negative independent '
            'data points'
        )

    def test_panels(self, default_panel):
        """ Test panel property behavior """
        putil.plot.Figure(panels=None)
        putil.plot.Figure(panels=default_panel)

    @pytest.mark.figure
    def test_panels_exceptions(self, default_panel):
        """ Test panel property exceptions """
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

    def test_title(self, default_panel):
        """ Test title property behavior """
        putil.plot.Figure(panels=default_panel, title=None)
        putil.plot.Figure(panels=default_panel, title='sec')
        obj = putil.plot.Figure(panels=default_panel, title='test')
        assert obj.title == 'test'

    @pytest.mark.figure
    def test_title_exceptions(self, default_panel):
        """ Test title property exceptions """
        putil.test.assert_exception(
            putil.plot.Figure,
            {'panels':default_panel, 'title':5},
            RuntimeError,
            'Argument `title` is not valid'
        )

    ### Miscellaneous
    @pytest.mark.figure
    def test_specified_figure_size_too_small_exceptions(self, default_panel):
        """ Test requested figure size is too small behavior """
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
            (
                'Figure size is too small: minimum width [5.6[1]|6.2]*, '
                'minimum height 2.6[6|8]'
            )
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
            (
                'Figure size is too small: minimum width [5.6[1]|6.2]*, '
                'minimum height 2.66'
            )
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
            (
                'Figure size is too small: minimum width [5.6[1]|6.2]*, '
                'minimum height 2.6[6|8]'
            )
        )

    @pytest.mark.figure
    def test_cannot_delete_attributes_exceptions(self, default_panel):
        """
        Test that del method raises an exception on all class attributes
        """
        obj = putil.plot.Figure(panels=default_panel)
        with pytest.raises(AttributeError) as excinfo:
            del obj.axes_list
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig_height
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.fig_width
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_axis_scale
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_var_label
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.indep_var_units
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.log_indep_axis
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.panels
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"
        with pytest.raises(AttributeError) as excinfo:
            del obj.title
        assert putil.test.get_exmsg(excinfo) == "can't delete attribute"

    def test_images(self, tmpdir):
        """ Compare images to verify correct plotting of figure """
        tmpdir.mkdir('test_images')
        images_dict_list = unittest_figure_images(
            mode='test', test_dir=str(tmpdir)
        )
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
                print(
                    'Reference image: file://{0}'.format(
                        os.path.realpath(ref_file_name)
                    )
                )
                print(
                    'Reference CI image: file://{0}'.format(
                        os.path.realpath(ref_ci_file_name)
                    )
                )
                print(
                    'Actual image: file://{0}'.format(
                        os.path.realpath(test_file_name)
                    )
                )
            assert result or result_ci
