# trace_ex_plot_panel.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
	""" Trace plot module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-x -k TestPanel '+os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..', '..', 'tests', 'test_plot.py'))):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'putil.plot.panel.Panel.'
		callable_names = ('__init__', 'series', 'primary_axis_label', 'secondary_axis_label', 'primary_axis_units', 'secondary_axis_units', 'log_axis', 'legend_props', 'show_indep_axis')
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
