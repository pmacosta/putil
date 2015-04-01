# trace_ex_plot_functions.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
	""" Trace plot module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-x -k TestParameterizedColorSpace '+os.path.realpath(os.path.join(os.path.realpath(__file__), '..', '..', '..', 'tests', 'test_plot.py'))):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'putil.plot.functions.'
		callable_names = (['parameterized_color_space'])
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
