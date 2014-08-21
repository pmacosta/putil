# pcsv_test.py	#pylint:disable=C0302
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
putil.pcsv unit tests
"""

import pytest

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

	def test_dfilter_wrong_type(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if the right exception is raised when parameter dfilter is of the wrong type """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		with pytest.raises(TypeError) as excinfo:
			putil.pcsv.CsvFile(file_name=file_name, dfilter='a')
		assert excinfo.value.message == 'Argument `dfilter` is of the wrong type'

	def test_dfilter_works(self, tmpdir, tmp_csv_file):	#pylint: disable=W0613,W0621,C0103,R0201
		""" Test if data filtering works """
		file_name = str(tmpdir.join('sub/tmp.csv'))
		obj = putil.pcsv.CsvFile(file_name=file_name, dfilter={'Ctrl':2, 'Ref':5})
		assert obj.data(filtered=True) == [[2, 5, 40]]

