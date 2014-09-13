# trace_ex_pcsv		pylint: disable=C0111
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

import tempfile

import putil.exh
import putil.misc
import putil.tree
import putil.pcsv

_EXH = None

def write_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('1,3,10\n')
	file_handle.write('1,4,20\n')
	file_handle.write('2,4,30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')

def trace_csvfile(no_print=False):
	""" Trace CsvFile class """
	global _EXH	#pylint: disable=W0603
	if not no_print:
		print putil.misc.pcolor('Tracing CsvFile', 'blue')
	_EXH = putil.exh.ExHandle(putil.pcsv.CsvFile)
	with putil.misc.TmpFile(write_file) as file_name:
		obj = putil.pcsv.CsvFile(file_name, dfilter={'Result':20})
	obj.add_dfilter({'Result':20})
	obj.dfilter = {'Result':20}
	obj.data()
	with tempfile.NamedTemporaryFile(delete=True) as fobj:
		obj.write(file_name=fobj.name, col=None, filtered=False, headers=True, append=False)
	_EXH.build_ex_tree(no_print=no_print)
	_EXH.print_ex_tree()
	_EXH.print_ex_table()

def trace_functions(no_print=False):
	""" Trace module-level functions """
	global _EXH	#pylint: disable=W0603
	if not no_print:
		print putil.misc.pcolor('Tracing putil.pcsv functions', 'blue')
	_EXH = putil.exh.ExHandle(putil.pcsv.write)
	with tempfile.NamedTemporaryFile(delete=True) as fobj:
		putil.pcsv.write(file_name=fobj.name, data=[['Col1', 'Col2'], [1, 2], [3, 4]], append=False)
	_EXH.build_ex_tree(no_print=no_print)
	_EXH.print_ex_tree()
	_EXH.print_ex_table()


if __name__ == '__main__':
	trace_csvfile()
	trace_functions()
