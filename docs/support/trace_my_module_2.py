# trace_my_module_2.py
# Option 2: use alrady written test bench
# pylint: disable=C0111,W0104
import copy
import putil.exdoc
import my_module
def trace_module(no_print=True):
	""" Trace my_module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		my_module.func('John')
		obj = my_module.MyClass()
		obj.value = 5
		obj.value
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
