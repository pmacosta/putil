# trace_ex_tree
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy
import pytest

import putil.exh
import putil.exdoc


def trace_module(no_print=True):
	""" Trace plot module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-s -vv -x ../tests/test_plot.py'):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		final_callable_names = tuple()
		module_prefix = 'putil.plot.BasicSource.'
		callable_names = ('__init__', 'indep_min', 'indep_max', 'indep_var', 'dep_var')
		final_callable_names += tuple([module_prefix+callable_name for callable_name in callable_names])
		module_prefix = 'putil.plot.CsvSource.'
		callable_names = ('__init__', 'file_name', 'dfilter', 'indep_col_label', 'dep_col_label', 'indep_min', 'indep_max', 'fproc', 'fproc_eargs', 'indep_var', 'dep_var')
		final_callable_names += tuple([module_prefix+callable_name for callable_name in callable_names])
		module_prefix = 'putil.plot.Series.'
		callable_names = ('__init__', 'data_source', 'label', 'color', 'marker', 'interp', 'line_style', 'secondary_axis')
		final_callable_names += tuple([module_prefix+callable_name for callable_name in callable_names])
		module_prefix = 'putil.plot.Panel.'
		callable_names = ('__init__', 'series', 'primary_axis_label', 'secondary_axis_label', 'primary_axis_units', 'secondary_axis_units', 'log_axis', 'legend_props', 'show_indep_axis')
		final_callable_names += tuple([module_prefix+callable_name for callable_name in callable_names])
		module_prefix = 'putil.plot.Figure.'
		callable_names = ('__init__', 'show', 'save', 'indep_var_label', 'indep_var_units', 'title', 'log_indep_axis', 'fig_width', 'fig_height', 'panels', 'fig', 'axes_list')
		final_callable_names += tuple([module_prefix+callable_name for callable_name in callable_names])
		final_callable_names += tuple(['putil.plot.parameterized_color_space'])
		for callable_name in final_callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
