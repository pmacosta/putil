# trace_ex_pcsv		pylint: disable=C0111
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212

import copy
import tempfile

import putil.exh
import putil.misc
import putil.pcsv

def write_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('1,3,10\n')
	file_handle.write('1,4,20\n')
	file_handle.write('2,4,30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')

def trace_csvfile(no_print=False):
	""" Trace CsvFile class """
	if not no_print:
		print putil.misc.pcolor('Tracing CsvFile', 'blue')
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	with putil.misc.TmpFile(write_file) as file_name:
		obj = putil.pcsv.CsvFile(file_name, dfilter={'Result':20})
	obj.add_dfilter({'Result':20})
	obj.dfilter = {'Result':20}
	obj.data()
	with tempfile.NamedTemporaryFile(delete=True) as fobj:
		obj.write(file_name=fobj.name, col=None, filtered=False, headers=True, append=False)
	exobj = putil.exh.get_exh_obj()
	exobj.build_ex_tree(obj=putil.pcsv.CsvFile, no_print=no_print)
	if not no_print:
		exobj.print_ex_tree()
		exobj.print_ex_table()
	return copy.deepcopy(exobj)

def trace_functions(no_print=False):
	""" Trace module-level functions """
	if not no_print:
		print putil.misc.pcolor('Tracing putil.pcsv functions', 'blue')
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	with tempfile.NamedTemporaryFile(delete=True) as fobj:
		putil.pcsv.write(file_name=fobj.name, data=[['Col1', 'Col2'], [1, 2], [3, 4]], append=False)
	exobj = putil.exh.get_exh_obj()
	exobj.build_ex_tree(obj=putil.pcsv.write, no_print=no_print)
	if not no_print:
		exobj.print_ex_tree()
		exobj.print_ex_table()
	return copy.deepcopy(exobj)


if __name__ == '__main__':
	trace_csvfile()
	trace_functions()
