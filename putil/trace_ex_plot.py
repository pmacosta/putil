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
		if pytest.main('-s -vv -x -k TestBasicSource ../tests/test_plot.py'):
			raise RuntimeError('Tracing did not complete successfully')
		if pytest.main('-s -vv -x -k TestCsvSource ../tests/test_plot.py'):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'putil.plot.BasicSource.'
		callable_names = ['__init__', 'indep_min', 'indep_max', 'indep_var', 'dep_var']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
