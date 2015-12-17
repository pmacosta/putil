#!/bin/bash
# compare-image-dirs.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

exe=../../docs/support/compare_images.py
dir1=./ref_images_1
dir2=./ref_images_2
file=figure_multiple_indep_axis_panel1_no_panel2_no_panel3_no.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_no_panel2_no_panel3_yes.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_no_panel2_yes_panel3_no.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_no_panel2_yes_panel3_yes.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_yes_panel2_no_panel3_no.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_yes_panel2_no_panel3_yes.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_yes_panel2_yes_panel3_no.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=figure_multiple_indep_axis_panel1_yes_panel2_yes_panel3_yes.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_filter_axis_series_in_primary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_linear_axis_series_in_both_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_linear_axis_series_in_primary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_linear_axis_series_in_secondary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_log_axis_series_in_both_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_log_axis_series_in_primary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_log_axis_series_in_secondary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_no_legend.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_single_axis_series_in_both_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_single_axis_series_in_primary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=panel_single_axis_series_in_secondary_axis.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_cubic_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_cubic_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_cubic_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_cubic_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_cubic_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_linreg_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_linreg_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_linreg_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_linreg_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_linreg_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_step_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_step_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_step_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_step_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_step_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_straight_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_straight_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_straight_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_straight_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_false_interp_straight_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_cubic_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_cubic_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_cubic_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_cubic_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_cubic_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_linreg_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_linreg_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_linreg_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_linreg_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_linreg_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_step_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_step_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_step_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_step_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_step_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_straight_line_style_dash-dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_straight_line_style_dashed.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_straight_line_style_dot.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_straight_line_style_none.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
file=series_marker_true_interp_straight_line_style_solid.png
if ! ${exe} -q ${dir1}/${file} ${dir2}/${file}; then
	echo "Directories are different"
	exit 1
fi
