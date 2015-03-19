# trace_ex_pcsv
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy, os, pytest

import putil.exdoc, putil.exh


def trace_module(no_print=False):
	""" Trace pcsv module exceptions """
	with putil.exdoc.ExDocCxt() as exdoc_obj:
		if pytest.main('-x '+os.path.abspath('../tests/test_pcsv.py')):
			raise RuntimeError('Tracing did not complete successfully')
	if not no_print:
		module_prefix = 'putil.pcsv.'
		callable_names = ['write', 'CsvFile.__init__', 'CsvFile.add_dfilter', 'CsvFile.data', 'CsvFile.reset_dfilter', 'CsvFile.write', 'CsvFile.dfilter', 'CsvFile.header']
		for callable_name in callable_names:
			callable_name = module_prefix+callable_name
			print '\nCallable: {0}'.format(callable_name)
			print exdoc_obj.get_sphinx_doc(callable_name)
			print '\n'
	return copy.copy(exdoc_obj)


if __name__ == '__main__':
	trace_module()
