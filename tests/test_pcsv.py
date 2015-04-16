# test_pcsv.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,R0201,W0232

import mock
import os
import pytest
import tempfile

import putil.misc
import putil.pcsv
import putil.test


###
# Tests for CsvFile
###
def write_file_empty(file_handle):
	file_handle.write('')


def write_cols_not_unique(file_handle):
	file_handle.write('Col1,Col2,Col3,Col1')


def write_no_data(file_handle):
	file_handle.write('Col1,Col2,Col3')


def write_data_start_file(file_handle):
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('"a","+inf","real"\n')
	file_handle.write('"b","c","d"\n')
	file_handle.write('2,"",30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')


def write_file(file_handle):
	file_handle.write('Ctrl,Ref,Result\n')
	file_handle.write('1,3,10\n')
	file_handle.write('1,4,20\n')
	file_handle.write('2,4,30\n')
	file_handle.write('2,5,40\n')
	file_handle.write('3,5,50\n')


def write_str_cols_file(file_handle):
	file_handle.write('Ctrl,Ref\n')
	file_handle.write('"nom",10\n')
	file_handle.write('"high",20\n')
	file_handle.write('"low",30\n')


class TestCsvFile(object):
	""" Tests for CsvFile class """
	def test_init_errors(self):
		"""
		Test that the right exceptions are raised when wrong parameter is
		passed to argument file_name
		"""
		# pylint: disable=C0103
		file_name = os.path.join(
			os.path.abspath(os.sep),
			'file',
			'does',
			'not',
			'exists.csv'
		)
		func_pointers = [
			(RuntimeError, 'File {0} is empty', write_file_empty),
			(RuntimeError, 'Column headers are not unique', write_cols_not_unique),
			(RuntimeError, 'File {0} has no valid data', write_no_data)
		]
		putil.test.assert_exception(
			putil.pcsv.CsvFile,
			{'file_name':5},
			RuntimeError,
			'Argument `file_name` is not valid'
		)
		putil.test.assert_exception(
			putil.pcsv.CsvFile,
			{'file_name':file_name},
			IOError,
			'File `{0}` could not be found'.format(file_name)
		)
		for extype, exmsg, fobj in func_pointers:
			with pytest.raises(extype) as excinfo:
				with putil.misc.TmpFile(fobj) as file_name:
					putil.pcsv.CsvFile(file_name=file_name)
			ref = (exmsg.format(file_name) if '{0}' in exmsg else exmsg)
			assert excinfo.value.message == ref

	def test_data_start(self):
		""" Test if the right row is picked for the data start """
		with putil.misc.TmpFile(write_data_start_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.data() == [[2, None, 30], [2, 5, 40], [3, 5, 50]]

	def test_dfilter_errors(self):
		"""
		Test if the right exception is raised when parameter dfilter is of
		the wrong type or some columns in the filter specification are not
		present in CSV file header
		"""
		with putil.misc.TmpFile(write_file) as file_name:
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':'a'},
				RuntimeError,
				'Argument `dfilter` is not valid'
			)
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':dict()},
				ValueError,
				'Argument `dfilter` is empty'
			)
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':{5:10}},
				RuntimeError,
				'Argument `dfilter` is not valid'
			)
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':{'aaa':5}},
				ValueError,
				'Column aaa not found in header'
			)
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':{'a':{'xx':2}}},
				RuntimeError,
				'Argument `dfilter` is not valid'
			)
			putil.test.assert_exception(
				putil.pcsv.CsvFile,
				{'file_name':file_name, 'dfilter':{'a':[3, {'xx':2}]}},
				RuntimeError,
				'Argument `dfilter` is not valid'
			)

	def test_dfilter_works(self):
		""" Test if data filtering works """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			assert obj.dfilter is None
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		assert obj.data(filtered=True) == [[2, 5, 40]]
		obj.dfilter = {'Ctrl':[2, 3], 'Ref':5}
		assert obj.data(filtered=True) == [[2, 5, 40], [3, 5, 50]]
		obj.dfilter = {'Result':100}
		assert obj.data(filtered=True) == []
		obj.dfilter = {'Result':'hello'}
		assert obj.data(filtered=True) == []
		obj.dfilter = None
		assert obj.dfilter is None
		# Test filtering by strings
		with putil.misc.TmpFile(write_str_cols_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':'low'})
			assert obj.data(filtered=True) == [['low', 30]]
			obj.add_dfilter({'Ctrl':'nom'})
			assert obj.data(filtered=True) == [['nom', 10], ['low', 30]]
			obj.add_dfilter({'Ctrl':'high'})
			assert obj.data(filtered=True) == [['nom', 10], ['high', 20], ['low', 30]]

	def test_reset_dfilter_works(self):
		""" Test if data filter reset works """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		assert obj.data(filtered=True) == [[2, 5, 40]]
		obj.reset_dfilter()
		assert obj.dfilter is None
		ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
		assert obj.data(filtered=True) == ref

	def test_add_dfilter_errors(self):
		"""
		Test if the right exception is raised when parameter dfilter is of the
		wrong type or some columns in the filter specification are not present
		in CSV file header
		"""
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		putil.test.assert_exception(
			obj.add_dfilter,
			{'dfilter':'a'},
			RuntimeError,
			'Argument `dfilter` is not valid'
		)
		putil.test.assert_exception(
			obj.add_dfilter,
			{'dfilter':dict()},
			ValueError,
			'Argument `dfilter` is empty'
		)
		putil.test.assert_exception(
			obj.add_dfilter,
			{'dfilter':{'aaa':5}},
			ValueError,
			'Column aaa not found in header'
		)
		putil.test.assert_exception(
			obj.add_dfilter,
			{'dfilter':{'a':{'xx':2}}},
			RuntimeError,
			'Argument `dfilter` is not valid'
		)
		putil.test.assert_exception(
			obj.add_dfilter,
			{'dfilter':{'a':[3, {'xx':2}]}},
			RuntimeError,
			'Argument `dfilter` is not valid'
		)

	def test_add_dfilter_works(self):
		""" Test if adding filters to existing data filtering works """
		# No previous filter
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			obj.add_dfilter(None)
			ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
			assert obj.data(filtered=True) == ref
			obj.add_dfilter({'Ctrl':1})
			obj.add_dfilter({'Result':20})
			assert obj.data(filtered=True) == [[1, 4, 20]]
			obj.reset_dfilter()
			obj.add_dfilter({'Result':20})
			assert obj.data(filtered=True) == [[1, 4, 20]]
			# Two single elements
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
			assert obj.data(filtered=True) == [[1, 4, 20]]
			obj.add_dfilter({'Result':40})
			assert obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40]]
			# Single element to list
			obj.dfilter = {'Result':[10, 30]}
			assert obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30]]
			obj.add_dfilter({'Result':50})
			assert obj.data(filtered=True) == [[1, 3, 10], [2, 4, 30], [3, 5, 50]]
			# List to list
			obj.dfilter = {'Result':[10, 20]}
			assert obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20]]
			obj.add_dfilter({'Result':[40, 50]})
			ref = [[1, 3, 10], [1, 4, 20], [2, 5, 40], [3, 5, 50]]
			assert obj.data(filtered=True) == ref
			# List to single element
			obj.dfilter = {'Result':20}
			assert obj.data(filtered=True) == [[1, 4, 20]]
			obj.add_dfilter({'Result':[40, 50]})
			assert obj.data(filtered=True) == [[1, 4, 20], [2, 5, 40], [3, 5, 50]]

	def test_header_works(self):
		""" Test if header attribute works """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.header == ['Ctrl', 'Ref', 'Result']

	def test_data_errors(self):
		""" Test if data() method raises the right exceptions """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		putil.test.assert_exception(
			obj.data,
			{'col':5},
			RuntimeError,
			'Argument `col` is not valid'
		)
		putil.test.assert_exception(
			obj.data,
			{'col':['a', 5]},
			RuntimeError,
			'Argument `col` is not valid'
		)
		putil.test.assert_exception(
			obj.data,
			{'col':'NotACol'},
			ValueError,
			'Column NotACol not found in header'
		)
		putil.test.assert_exception(
			obj.data,
			{'filtered':5},
			RuntimeError,
			'Argument `filtered` is not valid'
		)
		obj.data()
		obj.data(col=None, filtered=True)
		obj.data(col='Ctrl')
		obj.data(col=['Ctrl', 'Result'])

	def test_data_works(self):
		""" Test if data() method behaves properly """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		ref = [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]]
		assert obj.data() == ref
		assert obj.data(filtered=True) == [[1, 4, 20]]
		assert obj.data(col='Ref') == [[3], [4], [4], [5], [5]]
		assert obj.data(col='Ref', filtered=True) == [[4]]
		ref = [[1, 10], [1, 20], [2, 30], [2, 40], [3, 50]]
		assert obj.data(col=['Ctrl', 'Result']) == ref
		assert obj.data(col=['Ctrl', 'Result'], filtered=True) == [[1, 20]]

	def test_write_errors(self):
		"""
		Test if write() method raises the right exceptions when its arguments
		are of the wrong type or are badly specified
		"""
		some_file_name = os.path.join(os.path.abspath(os.sep), 'some', 'file')
		root_file = os.path.join(os.path.abspath(os.sep), 'test.csv')
		def mock_make_dir(file_name):
			if file_name == some_file_name:
				raise OSError(
					'File {0} could not be created'.format(some_file_name),
					'Permission denied'
				)
			elif file_name == root_file:
				raise IOError(
					'File {0} could not be created'.format(some_file_name),
					'Permission denied'
				)
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		putil.test.assert_exception(
			obj.write,
			{'file_name':5},
			RuntimeError,
			'Argument `file_name` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'headers':'a'},
			RuntimeError,
			'Argument `headers` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'append':'a'},
			RuntimeError,
			'Argument `append` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'col':5},
			RuntimeError,
			'Argument `col` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'col':['a', 5]},
			RuntimeError,
			'Argument `col` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'filtered':5},
			RuntimeError,
			'Argument `filtered` is not valid'
		)
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'col':'NotACol'},
			ValueError,
			'Column NotACol not found in header'
		)
		obj.dfilter = {'Result':100}
		putil.test.assert_exception(
			obj.write,
			{'file_name':some_file_name, 'filtered':True},
			ValueError,
			'There is no data to save to file'
		)
		obj.reset_dfilter()
		with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir):
			putil.test.assert_exception(
				obj.write,
				{'file_name':some_file_name},
				OSError,
				'File {0} could not be created: Permission denied'.format(some_file_name)
			)
			putil.test.assert_exception(
				obj.write,
				{'file_name':root_file},
				IOError,
				'File {0} could not be created: Permission denied'.format(root_file)
			)

	def test_write_works(self):
		""" Test if write() method behaves properly """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(file_name=file_name, col='Result', filtered=True, append=False)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		assert written_data == 'Result\r\n10\r\n20\r\n30\r\n40\r\n50\r\n'
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(file_name=file_name, append=False)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		ref = (
			'Ctrl,Ref,Result\r\n'
			'1,3,10\r\n'
			'1,4,20\r\n'
			'2,4,30\r\n'
			'2,5,40\r\n'
			'3,5,50\r\n'
		)
		assert written_data == ref
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.write(
				file_name=file_name,
				col=['Ctrl', 'Result'],
				filtered=True,
				headers=False,
				append=False
			)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		assert written_data == '1,10\r\n1,20\r\n2,30\r\n2,40\r\n3,50\r\n'
		with tempfile.NamedTemporaryFile() as fwobj:
			file_name = fwobj.name
			obj.reset_dfilter()
			obj.dfilter = {'Result':[10, 30]}
			obj.write(file_name=file_name, filtered=True, headers=True, append=False)
			obj.dfilter = {'Result':[20, 50]}
			obj.write(file_name=file_name, filtered=True, headers=False, append=True)
			with open(file_name, 'r') as frobj:
				written_data = frobj.read()
		ref = (
			'Ctrl,Ref,Result\r\n'
		    '1,3,10\r\n'
		    '2,4,30\r\n'
		    '1,4,20\r\n'
		    '3,5,50\r\n'
		)
		assert written_data == ref
		with putil.misc.TmpFile(write_data_start_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name)
			with tempfile.NamedTemporaryFile() as fwobj:
				file_name = fwobj.name
				obj.write(file_name=file_name)
				with open(file_name, 'r') as frobj:
					written_data = frobj.read()
		ref = "Ctrl,Ref,Result\r\n2,'',30\r\n2,5,40\r\n3,5,50\r\n"
		assert written_data == ref

	def test_cannot_delete_attributes(self):
		""" Test that del method raises an exception on all class attributes """
		with putil.misc.TmpFile(write_file) as file_name:
			obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		with pytest.raises(AttributeError) as excinfo:
			del obj.header
		assert excinfo.value.message == "can't delete attribute"
		with pytest.raises(AttributeError) as excinfo:
			del obj.dfilter
		assert excinfo.value.message == "can't delete attribute"


def test_write_function_errors():
	"""
	Test if write() function raises the right exceptions when its arguments
	are of the wrong type or are badly specified
	"""
	some_file_name = os.path.join(os.path.abspath(os.sep), 'some', 'file')
	def mock_make_dir(file_name):
		raise OSError(
			'File {0} could not be created'.format(file_name),
			'Permission denied'
		)
	some_file_name = os.path.join(os.path.abspath(os.sep), 'some', 'file')
	putil.test.assert_exception(
		putil.pcsv.write,
		{'file_name':5, 'data':[['Col1', 'Col2'], [1, 2]]},
		RuntimeError,
		'Argument `file_name` is not valid'
	)
	putil.test.assert_exception(
		putil.pcsv.write,
		{
			'file_name':some_file_name,
			'data':[['Col1', 'Col2'], [1, 2]],
			'append':'a'
		},
		RuntimeError,
		'Argument `append` is not valid'
	)
	with mock.patch('putil.misc.make_dir', side_effect=mock_make_dir):
		putil.test.assert_exception(
			putil.pcsv.write,
			{'file_name':some_file_name, 'data':[['Col1', 'Col2'], [1, 2]]},
			OSError,
			'File {0} could not be created: Permission denied'.format(some_file_name)
		)
	putil.test.assert_exception(
		putil.pcsv.write,
		{'file_name':'test.csv', 'data':[True, False]},
		RuntimeError,
		'Argument `data` is not valid'
	)
	putil.test.assert_exception(
		putil.pcsv.write,
		{'file_name':'test.csv', 'data':[[]]},
		ValueError,
		'There is no data to save to file'
	)


def test_write_function_works():
	""" Test if write() method behaves properly """
	with tempfile.NamedTemporaryFile() as fwobj:
		file_name = fwobj.name
		putil.pcsv.write(
			file_name,
			[['Input', 'Output'], [1, 2], [3, 4]],
			append=False
		)
		with open(file_name, 'r') as frobj:
			written_data = frobj.read()
	assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n'
	with tempfile.NamedTemporaryFile() as fwobj:
		file_name = fwobj.name
		putil.pcsv.write(
			file_name,
			[['Input', 'Output'], [1, 2], [3, 4]],
			append=False
		)
		putil.pcsv.write(file_name, [[5.0, 10]], append=True)
		with open(file_name, 'r') as frobj:
			written_data = frobj.read()
	assert written_data == 'Input,Output\r\n1,2\r\n3,4\r\n5.0,10\r\n'
