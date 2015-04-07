﻿# trace_my_module_2.py
# Option 2: manually use all callables to document
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,W0104
import copy, my_module_original, putil.exdoc
def trace_module(no_print=True):
	""" Trace my_module_original exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		try:
			my_module_original.func('John')
			obj = my_module_original.MyClass()
			obj.value = 5
			obj.value
		except:
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'my_module_original.'
		callable_names = ['func']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)

if __name__ == '__main__':
	trace_module(False)
