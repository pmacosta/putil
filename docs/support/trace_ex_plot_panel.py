# trace_ex_plot_panel.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, datetime, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
	""" Trace plot module exceptions """
	noption = os.environ.get('NOPTION', None)
	start_time = datetime.datetime.now()
	with putil.exdoc.ExDocCxt(exclude=['_pytest', 'execnet']) as exdoc_obj:
		if pytest.main('-x {0}-k TestPanel {1}'.format('{0} '.format(noption) if noption else '', os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'test_plot.py')))):
			raise RuntimeError('Tracing did not complete successfully')
	stop_time = datetime.datetime.now()
	if not no_print:
		print 'Auto-generatio of exceptions documentation time: {0}'.format(putil.misc.elapsed_time_string(start_time, stop_time))
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
