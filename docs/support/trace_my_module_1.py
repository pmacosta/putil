# trace_my_module_1.py
# Option 1: use already written test bench
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111
import copy, pytest, putil.exdoc
def trace_module(no_print=True):
	""" Trace my_module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-s -vv -x ../tests/test_my_module.py'):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'my_module.'
		callable_names = ['func']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)

if __name__ == '__main__':
	trace_module(False)
