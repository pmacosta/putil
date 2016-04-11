#!/usr/bin/env python
# gen_ref_images.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0912,R0914,R0915

# Standard library imports
from __future__ import print_function
import itertools
import math
import os
import sys
# PyPI imports
import numpy
# Putil imports
import putil.misc
import putil.plot


###
# Global variables
###
# Relative figure size
SCALE = 5
# Number of reference image sets
SETS = 12


###
# Functions
###
def def_file_names(mode, ref_dir, test_dir, img_name, olist):
    """ Generate image file names """
    test_fname = os.path.realpath(os.path.join(test_dir, img_name))
    if mode == 'ref':
        ref_fname = os.path.realpath(os.path.join(ref_dir, img_name))
    else:
        # Support incomplete sets of reference images to reduce size
        # of source tar ball
        temp_ref_fname = [
            os.path.realpath(os.path.join(ref_dir.format(num), img_name))
            for num in range(1, SETS+1)
        ]
        ref_fname = [item for item in temp_ref_fname if os.path.exists(item)]
    olist.append({'ref_fname':ref_fname, 'test_fname':test_fname})
    print(
        'Generating image {0}'.format(
            ref_fname if mode == 'ref' else test_fname
        )
    )
    return ref_fname if mode == 'ref' else test_fname


def setup_env(mode, test_dir):
    """ Define directories """
    mode = 'ref' if mode is None else mode.lower()
    ref_dir = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '..',
        'support',
        'ref_images{0}'.format('_{0}' if mode == 'test' else '')
    ) if (mode == 'test') or (not test_dir) else test_dir
    test_dir = (
        os.path.abspath(
            os.path.join('.', os.path.abspath(os.sep), 'test_images')
        )
        if test_dir is None else
        test_dir
    )
    return mode, ref_dir, test_dir


def unittest_series_images(mode=None, test_dir=None, _timeit=False):
    """ Images for Series() class """
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    #
    marker_list = [False, True]
    interp_list = ['STRAIGHT', 'STEP', 'CUBIC', 'LINREG']
    line_style_list = [None, '-', '--', '-.', ':']
    line_style_desc = {'-':'solid', '--':'dashed', '-.':'dash-dot', ':':'dot'}
    master_list = [marker_list, interp_list, line_style_list]
    comb_list = itertools.product(*master_list)
    olist = []
    print('')
    for marker, interp, line_style in comb_list:
        img_name = 'series_marker_{0}_interp_{1}_line_style_{2}.png'.format(
            'true' if marker else 'false',
            interp.lower(),
            'none' if not line_style else line_style_desc[line_style]
        )
        fname = def_file_names(mode, ref_dir, test_dir, img_name, olist)
        series_obj = putil.plot.Series(
            data_source=putil.plot.BasicSource(
                indep_var=numpy.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                dep_var=numpy.array(
                    [0.9, 2.5, 3, 3.5, 5.9, 6.6, 7.1, 7.9, 9.9, 10.5]
                )
            ),
            label='test series',
            marker='o' if marker else None,
            interp=interp,
            line_style=line_style
        )
        panel_obj = putil.plot.Panel(
            series=series_obj,
            primary_axis_label='Dependent axis',
            primary_axis_units='-',
        )
        fig_obj = putil.plot.Figure(
            panels=panel_obj,
            indep_var_label='Independent axis',
            indep_var_units='',
            log_indep_axis=False,
            fig_width=SCALE*4,
            fig_height=SCALE*3,
            title='marker: {0}\ninterp: {1}\nline_style: {2}'.format(
                marker,
                interp,
                line_style
            ),
        )
        fig_obj.save(fname)
        if _timeit:
            break
    return olist


def unittest_panel_images(mode=None, test_dir=None):
    """ Images for Panel() class """
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    #
    axis_type_list = ['single', 'linear', 'log', 'filter']
    series_in_axis_list = ['primary', 'secondary', 'both']
    master_list = [axis_type_list, series_in_axis_list]
    comb_list = itertools.product(*master_list)
    olist = []
    ds1_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([1, 2, 3, 4])
    )
    ds2_obj = putil.plot.BasicSource(
        indep_var=numpy.array([300, 400, 500, 600, 700]),
        dep_var=numpy.array([3, 4, 5, 6, 7])
    )
    ds3_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300]),
        dep_var=numpy.array([20, 40, 50])
    )
    ds4_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300]),
        dep_var=numpy.array([10, 25, 35])
    )
    ds5_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([10, 20, 30, 40])
    )
    ds6_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([20, 30, 40, 100])
    )
    ds7_obj = putil.plot.BasicSource(
        indep_var=numpy.array([200]),
        dep_var=numpy.array([50])
    )
    ds8_obj = putil.plot.BasicSource(
        indep_var=numpy.array([200]),
        dep_var=numpy.array([20])
    )
    indep_var = 1e3*numpy.array(
        [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70,
            80, 90, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
        ]
    )
    dep_var = numpy.array(
        [
            20*math.log10(
                math.sqrt(abs(1/(1+((1j*2*math.pi*freq)/(2*math.pi*1e4)))))
            )
        for freq in indep_var
        ]
    )
    ds9_obj = putil.plot.BasicSource(indep_var=indep_var, dep_var=dep_var)
    series1_obj = putil.plot.Series(
        data_source=ds1_obj,
        label='series 1',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='k'
    )
    series2_obj = putil.plot.Series(
        data_source=ds2_obj,
        label='series 2',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='b'
    )
    series3_obj = putil.plot.Series(
        data_source=ds3_obj,
        label='series 3',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='g', secondary_axis=True
    )
    series4_obj = putil.plot.Series(
        data_source=ds4_obj,
        label='series 4',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='r', secondary_axis=True
    )
    series5_obj = putil.plot.Series(
        data_source=ds5_obj,
        label='series 5',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='m', secondary_axis=True
    )
    series6_obj = putil.plot.Series(
        data_source=ds6_obj,
        label='series 6',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='c', secondary_axis=True
    )
    series7_obj = putil.plot.Series(
        data_source=ds7_obj,
        label='series 7',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='y'
    )
    series8_obj = putil.plot.Series(
        data_source=ds8_obj,
        label='series 8',
        marker='o',
        interp='STRAIGHT',
        line_style='--',
        color='k', secondary_axis=True
    )
    series9_obj = putil.plot.Series(
        data_source=ds9_obj,
        label='series 9',
        marker=None,
        interp='CUBIC',
        line_style='-',
        color='k'
    )
    seriesA_obj = putil.plot.Series(
        data_source=ds1_obj,
        label='',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='k'
    )
    seriesB_obj = putil.plot.Series(
        data_source=ds5_obj,
        label='',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='m', secondary_axis=True
    )
    for axis_type, series_in_axis in comb_list:
        img_name = 'panel_{0}_axis_series_in_{1}_axis.png'.format(
            axis_type,
            series_in_axis
        )
        if ((axis_type != 'filter') or
           ((axis_type == 'filter') and (series_in_axis == 'primary'))):
            fname = def_file_names(mode, ref_dir, test_dir, img_name, olist)
        if axis_type == 'linear':
            if series_in_axis == 'both':
                series_obj = [
                    series1_obj, series2_obj, series3_obj, series4_obj
                ]
            elif series_in_axis == 'primary':
                series_obj = [series1_obj, series2_obj]
            elif series_in_axis == 'secondary':
                series_obj = [series3_obj, series4_obj]
        elif axis_type == 'log':
            if series_in_axis == 'both':
                series_obj = [series1_obj, series5_obj]
            elif series_in_axis == 'primary':
                series_obj = [series1_obj]
            elif series_in_axis == 'secondary':
                series_obj = [series6_obj]
        if axis_type == 'single':
            if series_in_axis == 'both':
                series_obj = [series7_obj, series8_obj]
            elif series_in_axis == 'primary':
                series_obj = [series7_obj]
            elif series_in_axis == 'secondary':
                series_obj = [series8_obj]
        if axis_type == 'filter':
            if series_in_axis == 'both':
                pass
            elif series_in_axis == 'primary':
                series_obj = [series9_obj]
            elif series_in_axis == 'secondary':
                pass
        if ((axis_type != 'filter') or
           ((axis_type == 'filter') and (series_in_axis == 'primary'))):
            pflag = series_in_axis in ['primary', 'both']
            sflag = series_in_axis in ['secondary', 'both']
            panel_obj = putil.plot.Panel(
                series=series_obj,
                primary_axis_label='Primary axis' if pflag else None,
                primary_axis_units='-' if pflag else None,
                secondary_axis_label='Secondary axis' if sflag else None,
                secondary_axis_units='-' if sflag else None,
                # Hard-code it here to test series re-calculation
                # when set to True after
                log_dep_axis=False
            )
            panel_obj.log_dep_axis = True if axis_type == 'log' else False
            fig_obj = putil.plot.Figure(
                panels=panel_obj,
                indep_var_label='Independent axis',
                indep_var_units='',
                log_indep_axis=(axis_type == 'filter'),
                fig_width=SCALE*4,
                fig_height=SCALE*3,
                title='Axis: {0}\nSeries in axis: {1}'.format(
                    axis_type,
                    series_in_axis
                )
            )
            fig_obj.save(fname)
    # Panel with multiple series but no labels, should not print legend panel
    img_name = 'panel_no_legend.png'
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist)
    series_obj = [seriesA_obj, seriesB_obj]
    panel_obj = putil.plot.Panel(
        series=series_obj,
        primary_axis_label='Primary axis',
        primary_axis_units='-',
        secondary_axis_label='Secondary axis',
        secondary_axis_units='-',
        log_dep_axis=True
    )
    fig_obj = putil.plot.Figure(
        panels=panel_obj,
        indep_var_label='Independent axis',
        indep_var_units='',
        log_indep_axis=False,
        fig_width=SCALE*4,
        fig_height=SCALE*3,
        title='Panel no legend'
    )
    fig_obj.save(fname)
    return olist


def unittest_figure_images(mode=None, test_dir=None):
    """ Images for Figure() class """
    mode, ref_dir, test_dir = setup_env(mode, test_dir)
    #
    olist = []
    ds1_obj = putil.plot.BasicSource(
        indep_var=numpy.array([100, 200, 300, 400]),
        dep_var=numpy.array([1, 2, 3, 4])
    )
    ds2_obj = putil.plot.BasicSource(
        indep_var=numpy.array([300, 400, 500, 600, 700]),
        dep_var=numpy.array([3, 4, 5, 6, 7])
    )
    ds4_obj = putil.plot.BasicSource(
        indep_var=numpy.array([50, 100, 500, 1000, 1100]),
        dep_var=numpy.array([1.2e3, 100, 1, 300, 20])
    )
    series1_obj = putil.plot.Series(
        data_source=ds1_obj,
        label='series 1',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='k'
    )
    series2_obj = putil.plot.Series(
        data_source=ds2_obj,
        label='series 2',
        marker='o',
        interp='STRAIGHT',
        line_style='-',
        color='b',
        secondary_axis=True
    )
    series4_obj = putil.plot.Series(
        data_source=ds4_obj,
        label='series 3',
        marker='+',
        interp='CUBIC',
        line_style='-',
        color='r'
    )
    panel1_obj = putil.plot.Panel(
        series=series1_obj,
        # Test branch with no label in figure size calculation code
        primary_axis_label='',
        primary_axis_units='',
        secondary_axis_label='Secondary axis #1',
        secondary_axis_units='-',
        log_dep_axis=False
    )
    panel2_obj = putil.plot.Panel(
        series=series2_obj,
        primary_axis_label='Primary axis #2',
        primary_axis_units='-',
        secondary_axis_label='Secondary axis #2',
        secondary_axis_units='-',
        log_dep_axis=False
    )
    panel4_obj = putil.plot.Panel(
        series=series4_obj,
        primary_axis_label='Primary axis #3',
        primary_axis_units='-',
        secondary_axis_label='Secondary axis #3',
        secondary_axis_units='-',
        log_dep_axis=False
    )
    for num in range(0, 8):
        panel1_obj.display_indep_axis = num in [4, 5, 6, 7]
        panel2_obj.display_indep_axis = num in [2, 3, 6, 7]
        panel4_obj.display_indep_axis = num in [1, 3, 5, 7]
        panel1_flabel = 'yes' if panel1_obj.display_indep_axis else 'no'
        panel2_flabel = 'yes' if panel2_obj.display_indep_axis else 'no'
        panel4_flabel = 'yes' if panel4_obj.display_indep_axis else 'no'
        img_name = (
            'figure_multiple_indep_axis_panel1_'
            '{0}_panel2_{1}_panel3_{2}.png'.format(
                panel1_flabel,
                panel2_flabel,
                panel4_flabel
            )
        )
        fname = def_file_names(mode, ref_dir, test_dir, img_name, olist)
        fig_obj = putil.plot.Figure(
            panels=[panel1_obj, panel2_obj, panel4_obj],
            indep_var_label='Independent axis' if not num else '',
            indep_var_units='',
            log_indep_axis=False,
            fig_width=SCALE*4,
            fig_height=SCALE*3,
            title=(
                'Multiple independent axis\n'
                'Panel 1 {0}, panel 2 {1}, panel 3 {2}'.format(
                   panel1_flabel,
                   panel2_flabel,
                   'yes by omission' if not num else panel4_flabel
                )
            )
        )
        fig_obj.save(fname)
    # Figure without anything but tick marks and series without
    # predetermined size
    img_name = 'figure_basic.png'
    fname = def_file_names(mode, ref_dir, test_dir, img_name, olist)
    source_obj = putil.plot.BasicSource(
        numpy.array(list(range(1, 6))), numpy.array([1, 2, 3, 10, 4])
    )
    series_obj = putil.plot.Series(source_obj, label='')
    panel_obj = putil.plot.Panel(series_obj)
    figure_obj = putil.plot.Figure(panel_obj)
    figure_obj.save(fname)
    return olist


def main(argv):
    """ Main function, generate images """
    if len(argv) == 0:
        unittest_series_images(mode='ref')
        unittest_panel_images(mode='ref')
        unittest_figure_images(mode='ref')
    else:
        unittest_series_images(mode='ref', test_dir=argv[0])
        unittest_panel_images(mode='ref', test_dir=argv[0])
        unittest_figure_images(mode='ref', test_dir=argv[0])


if __name__ == '__main__':
    main(sys.argv[1:])
