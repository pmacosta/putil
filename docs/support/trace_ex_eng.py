# trace_ex_eng.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, datetime, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=True):
	""" Trace eng module exceptions """
	noption = os.environ.get('NOPTION', None)
	start_time = datetime.datetime.now()
	with putil.exdoc.ExDocCxt(exclude=['_pytest', 'execnet']) as exdoc_obj:
		if pytest.main('-x {0}{1}'.format('{0} '.format(noption) if noption else '', os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'tests', 'test_eng.py')))):
			raise RuntimeError('Tracing did not complete successfully')
	stop_time = datetime.datetime.now()
	if not no_print:
		print 'Auto-generatio of exceptions documentation time: {0}'.format(putil.misc.elapsed_time_string(start_time, stop_time))
		module_prefix = 'putil.eng.'
		callable_names = ['peng', 'peng_float', 'peng_frac', 'peng_int', 'peng_mant', 'peng_power', 'peng_suffix', 'peng_suffix_math']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module(False)
