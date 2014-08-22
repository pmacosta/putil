# pcsv_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcsv unit tests
"""

import pytest
import tempfile

import putil.pcsv


###
# Tests for CsvFile
###
@pytest.fixture
def tmp_csv_file_empty(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp_empty.csv')
	file_handle.write('', mode='w')
	return True

@pytest.fixture
def tmp_csv_file_cols_not_unique(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp_cols_not_unique.csv')
	file_handle.write('Col1,Col2,Col3,Col1', mode='w')
	return True

@pytest.fixture
def tmp_csv_file_no_data(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp_no_data.csv')
	file_handle.write('Col1,Col2,Col3', mode='w')
	return True

@pytest.fixture
def tmp_csv_data_start(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp_data_start.csv')
	file_handle.write('Ctrl,Ref,Result\n', mode='w')
	file_handle.write('"a","+inf","real"\n', mode='a')
	file_handle.write('"b","c","d"\n', mode='a')
	file_handle.write('2,"",30\n', mode='a')
	file_handle.write('2,5,40\n', mode='a')
	file_handle.write('3,5,50\n', mode='a')
	return True

@pytest.fixture
def tmp_csv_file(tmpdir):
	""" Fixture to create temporary CSV file for testing purposes """
	file_handle = tmpdir.mkdir('sub').join('tmp.csv')
	file_handle.write('Ctrl,Ref,Result\n', mode='w')
	file_handle.write('1,3,10\n', mode='a')
	file_handle.write('1,4,20\n', mode='a')
	file_handle.write('2,4,30\n', mode='a')
	file_handle.write('2,5,40\n', mode='a')
	file_handle.write('3,5,50\n', mode='a')
	return True

class TestCsvFile(object):	#pylint: disable=W0232
	""" Tests for CsvFile class """
	def test_file_name_wrong_type(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the CSV file does not exist """
		with pytest.raises(TypeError) as excinfo:
			putil.pcsv.CsvFile(file_name=5)
		assert excinfo.value.message == 'Argument `file_name` is of the wrong type'

	def test_file_does_not_exist(self):	#pylint: disable=C0103,R0201
		""" Test that the rigth exception is raised when the CSV file does not exist """
		file_name = '/file/does/not/exist.csv'
		with pytest.raises(IOError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name)
		assert excinfo.value.message == 'File {0} could not be found'.format(file_name)

	def test_file_empty(self, tmpdir, tmp_csv_file_empty):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when the CSV file exists but is empty """
		file_name = str(tmpdir.join('sub/tmp_empty.csv'))
		with pytest.raises(RuntimeError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name)
		assert excinfo.value.message == 'File {0} is empty'.format(file_name)

	def test_header_cols_not_unique(self, tmpdir, tmp_csv_file_cols_not_unique):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when the header has duplicate column names """
		file_name = str(tmpdir.join('sub/tmp_cols_not_unique.csv'))
		with pytest.raises(RuntimeError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name)
		assert excinfo.value.message == 'Column headers are not unique'

	def test_no_data_in_file(self, tmpdir, tmp_csv_file_no_data):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when the file has a header but no data """
		file_name = str(tmpdir.join('sub/tmp_no_data.csv'))
		with pytest.raises(RuntimeError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name)
		assert excinfo.value.message == 'File {0} has no data'.format(file_name)

	def test_data_start(self, tmpdir, tmp_csv_data_start):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right row is picked for the data start """
		file_name = str(tmpdir.join('sub/tmp_data_start.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.data() == [[2, None, 30], [2, 5, 40], [3, 5, 50]]

	def test_dfilter_errors(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when parameter dfilter is of the wrong type or some columns in the filter specification are not present in CSV file header """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name, dfilter='a')
		test_list.append(excinfo.value.message == 'Argument `dfilter` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name, dfilter={})
		test_list.append(excinfo.value.message == 'Argument `dfilter` is empty')
		with pytest.raises(ValueError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name, dfilter={'aaa':5})
		test_list.append(excinfo.value.message == 'Column aaa not found in header')
		assert test_list == 3*[True]

	def test_dfilter_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if data filtering works """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		obj = putil.pcsv.CsvFile(file_name=file_name)
		test_list.append(obj.dfilter == None)
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		test_list.append(obj.data(filtered=True) == [[2, 5, 40]])
		obj.dfilter = {'Ctrl':[2, 3], 'Ref':5}
		test_list.append(obj.data(filtered=True) == [[2, 5, 40], [3, 5, 50]])
		obj.dfilter = {'Result':100}
		test_list.append(obj.data(filtered=True) == [])
		obj.dfilter = None
		test_list.append(obj.dfilter == None)
		assert test_list == 5*[True]

	def test_reset_dfilter_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if data filter reset works """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		test_list.append(obj.data(filtered=True) == [[2, 5, 40]])
		obj.reset_dfilter()
		test_list.append(obj.dfilter == None)
		test_list.append(obj.data(filtered=True) == [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]])
		assert test_list == 3*[True]

	def test_add_dfilter_errors(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when parameter dfilter is of the wrong type or some columns in the filter specification are not present in CSV file header """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		obj = putil.pcsv.CsvFile(file_name=file_name)
		with pytest.raises(TypeError) as excinfo:
			obj.add_dfilter('a')
		test_list.append(excinfo.value.message == 'Argument `dfilter` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			obj.add_dfilter({})
		test_list.append(excinfo.value.message == 'Argument `dfilter` is empty')
		with pytest.raises(ValueError) as excinfo:
			obj.add_dfilter({'aaa':5})
		test_list.append(excinfo.value.message == 'Column aaa not found in header')
		assert test_list == 3*[True]

	def test_add_dfilter_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if adding filters to existing data filtering works """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
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
		assert test_list == 8*[True]

	def test_header_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if header attribute works """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name)
		assert obj.header == ['Ctrl', 'Ref', 'Result']

	def test_data_errors(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if data() method raises the right exceptions """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		with pytest.raises(TypeError) as excinfo:
			obj.data(col=5)
		test_list.append(excinfo.value.message == 'Argument `col` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.data(col=['a', 5])
		test_list.append(excinfo.value.message == 'Argument `col` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.data(filtered=5)
		test_list.append(excinfo.value.message == 'Argument `filtered` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			obj.data(col='NotACol')
		test_list.append(excinfo.value.message == 'Column NotACol not found in header')
		# These should not raise any errors
		obj.data()
		obj.data(col=None, filtered=True)
		obj.data(col='Ctrl')
		obj.data(col=['Ctrl', 'Result'])
		assert test_list == 4*[True]

	def test_data_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if data() method behaves properly """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		test_list = list()
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		test_list.append(obj.data() == [[1, 3, 10], [1, 4, 20], [2, 4, 30], [2, 5, 40], [3, 5, 50]])
		test_list.append(obj.data(filtered=True) == [[1, 4, 20]])
		test_list.append(obj.data(col='Ref') == [[3], [4], [4], [5], [5]])
		test_list.append(obj.data(col='Ref', filtered=True) == [[4]])
		test_list.append(obj.data(col=['Ctrl', 'Result']) == [[1, 10], [1, 20], [2, 30], [2, 40], [3, 50]])
		test_list.append(obj.data(col=['Ctrl', 'Result'], filtered=True) == [[1, 20]])
		assert test_list == 6*[True]

	def test_write_errors(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if write() method raises the right exceptions when its arguments are of the wrong type or are badly specified """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name)
		test_list = list()
		with pytest.raises(TypeError) as excinfo:
			obj.write(file_name=5)
		test_list.append(excinfo.value.message == 'Argument `file_name` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.write(file_name='/some/file', append='a')
		test_list.append(excinfo.value.message == 'Argument `append` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.write(file_name='/some/file', col=5)
		test_list.append(excinfo.value.message == 'Argument `col` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.write(file_name='/some/file', col=['a', 5])
		test_list.append(excinfo.value.message == 'Argument `col` is of the wrong type')
		with pytest.raises(TypeError) as excinfo:
			obj.write(file_name='/some/file', filtered=5)
		test_list.append(excinfo.value.message == 'Argument `filtered` is of the wrong type')
		with pytest.raises(ValueError) as excinfo:
			obj.write(file_name='/some/file', col='NotACol')
		test_list.append(excinfo.value.message == 'Column NotACol not found in header')
		obj.dfilter = {'Result':100}
		with pytest.raises(ValueError) as excinfo:
			obj.write(file_name='/some/file', filtered=True)
		test_list.append(excinfo.value.message == 'There is no data to save to file')
		with pytest.raises(OSError) as excinfo:
			obj.write(file_name='/some/file')
		test_list.append(excinfo.value.message == 'File /some/file could not be created: Permission denied')
		assert test_list == 8*[True]

	def test_write_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if write() method behaves properly """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name)
		with tempfile.NamedTemporaryFile() as fobj:
			file_name = fobj.name
			obj.write(file_name=file_name, col='Result', filtered=True, append=False)

	def test_cannot_delete_attributes(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test that del method raises an exception on all class attributes """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Result':20})
		test_list = list()
		with pytest.raises(AttributeError) as excinfo:
			del obj.header
		test_list.append(excinfo.value.message == "can't delete attribute")
		with pytest.raises(AttributeError) as excinfo:
			del obj.dfilter
		test_list.append(excinfo.value.message == "can't delete attribute")
		assert test_list == 2*[True]

