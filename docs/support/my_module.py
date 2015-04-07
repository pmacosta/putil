# my_module_original.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,R0903,W0105


###
# Exception tracing initialization code
###
"""
[[[cog
import trace_my_module_2
exobj_my_module = trace_my_module_2.trace_module()
]]]
[[[end]]]
"""

import putil.exh

def func(name):
	"""
	Prints your name

	:param   name: Name to print
	:type name: string

	.. [[[cog cog.out(exobj_my_module.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for my_module_original.func

	:raises: TypeError (Argument \`name\` is not valid)

	.. [[[end]]]

	"""
	exhobj = putil.exh.get_or_create_exh_obj()
	exhobj.add_exception(
		exname='illegal_name',
		extype=TypeError,
		exmsg='Argument `name` is not valid'
	)
	exhobj.raise_exception_if(
		exname='illegal_name',
		condition=not isinstance(name, str)
	)
	print 'My name is {0}'.format(name)

class MyClass(object):
	"""
	Stores a value

	:param	value: value
	:type	value: integer

	.. [[[cog cog.out(exobj_my_module.get_sphinx_autodoc()) ]]]
	.. [[[end]]]
	"""
	def __init__(self, value=None):
		self._exhobj = putil.exh.get_or_create_exh_obj()
		self._value = None if not value else value

	def _get_value(self):
		self._exhobj.add_exception(
			exname='not_set',
			extype=RuntimeError,
			exmsg='Attribute `value` not set'
		)
		self._exhobj.raise_exception_if(
			exname='not_set',
			condition=not self._value
		)
		return self._value

	def _set_value(self, value):
		self._exhobj.add_exception(
			exname='illegal',
			extype=RuntimeError,
			exmsg='Argument `value` is not valid'
		)
		self._exhobj.raise_exception_if(
			exname='illegal',
			condition=not isinstance(value, int)
		)
		self._value = value

	value = property(_get_value, _set_value)
	"""
	Sets or returns a value

	:type:	integer
	:rtype:	integer or None

	.. [[[cog cog.out(exobj_my_module.get_sphinx_autodoc()) ]]]
	.. Auto-generated exceptions documentation for my_module_original.MyClass.value

	:raises:
	 * When assigned

	   * RuntimeError (Argument \`value\` is not valid)

	 * When retrieved

	   * RuntimeError (Attribute \`value\` not set)

	.. [[[end]]]
	"""
