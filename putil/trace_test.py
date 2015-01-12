# trace_ex_pcsv
# Copyright (c) 2013-2014 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=W0212,C0111

import copy
import pytest

import putil.exh
import putil.exdoc

def trace_csvfile(no_print=False):
	""" Trace CsvFile class """
	putil.exh.set_exh_obj(putil.exh.ExHandle())
	pytest.main('-s -vv -x -k TestCsvFile ../tests/test_pcsv.py')
	exobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), module_name='putil.pcsv.CsvFile', no_print=no_print)
	if not no_print:
		exobj.print_ex_tree()
		exobj.print_ex_table()
	return copy.copy(exobj)

	# if not no_print:
	# 	print putil.misc.pcolor('Tracing CsvFile', 'blue')
	# putil.exh.set_exh_obj(putil.exh.ExHandle())
	# with putil.misc.TmpFile(write_file) as file_name:
	# 	obj = putil.pcsv.CsvFile(file_name, dfilter={'Result':20})
	# obj.add_dfilter({'Result':20})
	# obj.dfilter = {'Result':20}
	# obj.data()
	# with tempfile.NamedTemporaryFile(delete=True) as fobj:
	# 	obj.write(file_name=fobj.name, col=None, filtered=False, headers=True, append=False)
	# exobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=no_print)
	# if not no_print:
	# 	exobj.print_ex_tree()
	# 	exobj.print_ex_table()
	# return copy.copy(exobj)

# def trace_functions(no_print=False):
# 	""" Trace module-level functions """
# 	if not no_print:
# 		print putil.misc.pcolor('Tracing putil.pcsv functions', 'blue')
# 	putil.exh.set_exh_obj(putil.exh.ExHandle())
# 	with tempfile.NamedTemporaryFile(delete=True) as fobj:
# 		putil.pcsv.write(file_name=fobj.name, data=[['Col1', 'Col2'], [1, 2], [3, 4]], append=False)
# 	exobj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), no_print=no_print)
# 	if not no_print:
# 		exobj.print_ex_tree()
# 		exobj.print_ex_table()
# 	return copy.copy(exobj)


if __name__ == '__main__':
	trace_csvfile()
	#trace_functions()
