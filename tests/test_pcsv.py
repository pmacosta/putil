# test_pcsv.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcsv unit tests
"""

import pytest
import tempfile

import putil.misc
import putil.pcsv
import putil.test

###
# Tests for CsvFile
###
def write_file_empty(file_handle):	#pylint: disable=C0111
	file_handle.write('')

def write_cols_not_unique(file_handle):	#pylint: disable=C0111
	file_handle.write('Col1,Col2,Col3,Col1')

def write_no_data(file_handle):	#pylint: disable=C0111
	file_handle.write('Col1,Col2,Col3')

def write_data_start_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('"a","+inf","real"\n')
	file_handle.write('"b","c","d"\n')
	file_handle.write('2,"",30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')

def write_file(file_handle):	#pylint: disable=C0111
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('1,3,10\n')
	file_handle.write('1,4,20\n')
	file_handle.write('2,4,30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')

class TestCsvFile(object):	#pylint: disable=W0232
	""" Tests for CsvFile class """
	def test_init_errors(self):	#pylint: disable=C0103,R0201
		""" Test that the right exceptions are raised when wrong parameter is passed to argument file_name """
		test_list = list()
		file_name = '/file/does/not/exist.csv'
		func_pointers = [(RuntimeError, 'File {0} is empty', write_file_empty), (RuntimeError, 'Column headers are not unique', write_cols_not_unique), (RuntimeError, 'File {0} has no valid data', write_no_data)]
		test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':5}, RuntimeError, 'Argument `file_name` is not valid'))
		test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name}, IOError, 'File `{0}` could not be found'.format(file_name)))
		for extype, exmsg, fobj in func_pointers:
			with pytest.raises(extype) as excinfo:
				with putil.misc.TmpFile(fobj) as file_name:
					putil.pcsv.CsvFile(file_name=file_name)
			test_list.append(excinfo.value.message == (exmsg.format(file_name) if '{0}' in exmsg else exmsg))
		assert test_list == len(test_list)*[True]

	def test_data_start(self):	#pylint: disable=R0201
		""" Test if the right row is picked for the data start """
		with putil.misc.TmpFile(write_data_start_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.data() == [[2, None, 30], [2, 5, 40], [3, 5, 50]]

	def test_dfilter_errors(self):	#pylint: disable=R0201
		""" Test if the right exception is raised when parameter dfilter is of the wrong type or some columns in the filter specification are not present in CSV file header """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':'a'}, RuntimeError, 'Argument `dfilter` is not valid'))
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':dict()}, ValueError, 'Argument `dfilter` is empty'))
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':{5:10}}, RuntimeError, 'Argument `dfilter` is not valid'))
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':{'aaa':5}}, ValueError, 'Column aaa not found in header'))
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':{'a':{'xx':2}}}, RuntimeError, 'Argument `dfilter` is not valid'))
			test_list.append(putil.test.trigger_exception(putil.pcsv.CsvFile, {'file_name':file_name, 'dfilter':{'a':[3, {'xx':2}]}}, RuntimeError, 'Argument `dfilter` is not valid'))
		assert test_list == len(test_list)*[True]

	def test_dfilter_works(self):	#pylint: disable=R0201
		""" Test if data filtering works """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			test_list.append(obj.dfilter == None)
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		test_list.append(obj.data(filtered=True) == [[2, 5, 40]])
		obj.dfilter = {'Ctrl':[2, 3], 'Ref':5}
		test_list.append(obj.data(filtered=True) == [[2, 5, 40], [3, 5, 50]])
		obj.dfilter = {'Result':100}
		test_list.append(obj.data(filtered=True) == [])
		obj.dfilter = {'Result':'hello'}
		test_list.append(obj.data(filtered=True) == [])
		obj.dfilter = None
		test_list.append(obj.dfilter == None)
		assert test_list == len(test_list)*[True]

	def test_reset_dfilter_works(self):	#pylint: disable=R0201
		""" Test if data filter reset works """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		test_list.append(obj.data(filtered=True) == [[2, 5, 40]])
		obj.reset_dfilter()
		test_list.append(obj.dfilter == None)
		test_list.append(obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]])
		assert test_list == len(test_list)*[True]

	def test_add_dfilter_errors(self):	#pylint: disable=R0201
		""" Test if the right exception is raised when parameter dfilter is of the wrong type or some columns in the filter specification are not present in CSV file header """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		test_list.append(putil.test.trigger_exception(obj.add_dfilter, {'dfilter':'a'}, RuntimeError, 'Argument `dfilter` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.add_dfilter, {'dfilter':dict()}, ValueError, 'Argument `dfilter` is empty'))
		test_list.append(putil.test.trigger_exception(obj.add_dfilter, {'dfilter':{'aaa':5}}, ValueError, 'Column aaa not found in header'))
		test_list.append(putil.test.trigger_exception(obj.add_dfilter, {'dfilter':{'a':{'xx':2}}}, RuntimeError, 'Argument `dfilter` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.add_dfilter, {'dfilter':{'a':[3, {'xx':2}]}}, RuntimeError, 'Argument `dfilter` is not valid'))
		assert test_list == len(test_list)*[True]

	def test_add_dfilter_works(self):	#pylint: disable=R0201
		""" Test if adding filters to existing data filtering works """
		test_list = list()
		# No previous filter
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			obj.add_dfilter(None)
			test_list.append(obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]])
			obj.add_dfilter({'Ctrl':1})
			obj.add_dfilter({'Result':20})
			test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
			obj.reset_dfilter()
			obj.add_dfilter({'Result':20})
			test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
			# Two single elements
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
			test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
			obj.add_dfilter({'Result':40})
			test_list.append(obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40]])
			# Single element to list
			obj.dfilter = {'Result':[10, 30]}
			test_list.append(obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30]])
			obj.add_dfilter({'Result':50})
			test_list.append(obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30], [3, 5, 50]])
			# List to list
			obj.dfilter = {'Result':[10, 20]}
			test_list.append(obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20]])
			obj.add_dfilter({'Result':[40, 50]})
			test_list.append(obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20], [2, 5, 40], [3, 5, 50]])
			# List to single element
			obj.dfilter = {'Result':20}
			test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
			obj.add_dfilter({'Result':[40, 50]})
			test_list.append(obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40], [3, 5, 50]])
		assert test_list == len(test_list)*[True]

	def test_header_works(self):	#pylint: disable=R0201
		""" Test if header attribute works """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.header == ['Ctrl', 'Ref', 'Result']

	def test_data_errors(self):	#pylint: disable=R0201
		""" Test if data() method raises the right exceptions """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		test_list.append(putil.test.trigger_exception(obj.data, {'col':5}, RuntimeError, 'Argument `col` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.data, {'col':['a', 5]}, RuntimeError, 'Argument `col` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.data, {'col':'NotACol'}, ValueError, 'Column NotACol not found in header'))
		test_list.append(putil.test.trigger_exception(obj.data, {'filtered':5}, RuntimeError, 'Argument `filtered` is not valid'))
		obj.data()
		obj.data(col=None, filtered=True)
		obj.data(col='Ctrl')
		obj.data(col=['Ctrl', 'Result'])
		assert test_list == len(test_list)*[True]

	def test_data_works(self):	#pylint: disable=R0201
		""" Test if data() method behaves properly """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		test_list.append(obj.data() == [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]])
		test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
		test_list.append(obj.data(col='Ref') == [[3], [4], [4], [5], [5]])
		test_list.append(obj.data(col='Ref', filtered=True) == [[4]])
		test_list.append(obj.data(col=['Ctrl', 'Result']) == [[1, 10], [1, 20], [2, 30], [2, 40], [3, 50]])
		test_list.append(obj.data(col=['Ctrl', 'Result'], filtered=True) == [[1, 20]])
		assert test_list == len(test_list)*[True]

	def test_write_errors(self):	#pylint: disable=R0201
		""" Test if write() method raises the right exceptions when its arguments are of the wrong type or are badly specified """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':5}, RuntimeError, 'Argument `file_name` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'headers':'a'}, RuntimeError, 'Argument `headers` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'append':'a'}, RuntimeError, 'Argument `append` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'col':5}, RuntimeError, 'Argument `col` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'col':['a', 5]}, RuntimeError, 'Argument `col` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'filtered':5}, RuntimeError, 'Argument `filtered` is not valid'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'col':'NotACol'}, ValueError, 'Column NotACol not found in header'))
		obj.dfilter = {'Result':100}
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file', 'filtered':True}, ValueError, 'There is no data to save to file'))
		obj.reset_dfilter()
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/some/file'}, OSError, 'File /some/file could not be created: Permission denied'))
		test_list.append(putil.test.trigger_exception(obj.write, {'file_name':'/test.csv'}, IOError, 'File /test.csv could not be created: Permission denied'))
		assert test_list == len(test_list)*[True]

	def test_write_works(self):	#pylint: disable=R0201
		""" Test if write() method behaves properly """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(file_name=file_name, col='Result', filtered=True, append=False)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		test_list.append(written_data == 'Result\r\n10\r\n20\r\n30\r\n40\r\n50\r\n')
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(file_name=file_name, append=False)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		test_list.append(written_data == 'Ctrl,Ref,Result\r\n1,3,10\r\n1,4,20\r\n2,4,30\r\n2,5,40\r\n3,5,50\r\n')
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(file_name=file_name, col=['Ctrl', 'Result'], filtered=True, headers=False, append=False)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		test_list.append(written_data == '1,10\r\n1,20\r\n2,30\r\n2,40\r\n3,50\r\n')
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.reset_dfilter()
			obj.dfilter = {'Result':[10, 30]}
			obj.write(file_name=file_name, filtered=True, headers=True, append=False)
			obj.dfilter = {'Result':[20, 50]}
			obj.write(file_name=file_name, filtered=True, headers=False, append=True)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		test_list.append(written_data == 'Ctrl,Ref,Result\r\n1,3,10\r\n2,4,30\r\n1,4,20\r\n3,5,50\r\n')
		with putil.misc.TmpFile(write_data_start_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			with tempfile.NamedTemporaryFile() as fwobj:
				file_name = fwobj.name
				obj.write(file_name=file_name)
				with open(file_name, 'r') as frobj:
					written_data = frobj.read()
		test_list.append(written_data == "Ctrl,Ref,Result\r\n2,'',30\r\n2,5,40\r\n3,5,50\r\n")
		assert test_list == len(test_list)*[True]

	def test_cannot_delete_attributes(self):	#pylint: disable=R0201
		""" Test that del method raises an exception on all class attributes """
		test_list = list()
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		with pytest.raises(AttributeError) as excinfo:
			del obj.header
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.dfilter
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == len(test_list)*[True]


def test_write_function_errors():	#pylint: disable=R0201
	""" Test if write() function raises the right exceptions when its arguments are of the wrong type or are badly specified """
	test_list = list()
	test_list.append(putil.test.trigger_exception(putil.pcsv.write, {'file_name':5, 'data':[['Col1', 'Col2'], [1, 2]]}, RuntimeError, 'Argument `file_name` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.pcsv.write, {'file_name':'/some/file', 'data':[['Col1', 'Col2'], [1, 2]], 'append':'a'}, RuntimeError, 'Argument `append` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.pcsv.write, {'file_name':'/some/file', 'data':[['Col1', 'Col2'], [1, 2]]}, OSError, 'File /some/file could not be created: Permission denied'))
	test_list.append(putil.test.trigger_exception(putil.pcsv.write, {'file_name':'test.csv', 'data':[True, False]}, RuntimeError, 'Argument `data` is not valid'))
	test_list.append(putil.test.trigger_exception(putil.pcsv.write, {'file_name':'test.csv', 'data':[[]]}, ValueError, 'There is no data to save to file'))
	assert test_list == len(test_list)*[True]

def test_write_function_works():	#pylint: disable=R0201
	""" Test if write() method behaves properly """
	test_list = list()
	with tempfile.NamedTemporaryFile() as fwobj:
		file_name = fwobj.name
		putil.pcsv.write(file_name, [['Input', 'Output'], [1, 2], [3, 4]], append=False)
		with open(file_name, 'r') as frobj:
			written_data = frobj.read()
	test_list.append(written_data == 'Input,Output\r\n1,2\r\n3,4\r\n')
	with tempfile.NamedTemporaryFile() as fwobj:
		file_name = fwobj.name
		putil.pcsv.write(file_name, [['Input', 'Output'], [1, 2], [3, 4]], append=False)
		putil.pcsv.write(file_name, [[5.0, 10]], append=True)
		with open(file_name, 'r') as frobj:
			written_data = frobj.read()
	test_list.append(written_data == 'Input,Output\r\n1,2\r\n3,4\r\n5.0,10\r\n')
	assert test_list == len(test_list)*[True]
