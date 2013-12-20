"""
Utility classes, methods and functions to handle comma-delimited file as a quasi database
"""

import os
import csv

class CsvFile(object):
	"""
	Read CSV files, filter and retrieve information. First row must contain headers, the rest of the data must be numbers
	"""
	def __init__(self, file_name):
		if isinstance(file_name, str) is False:
			msg = 'file_name has to be a string'
			raise TypeError(msg)
		if os.path.exists(file_name) is False:
			msg = 'File '+file_name+' could not be found'
			raise IOError(msg)
		self.current_header = None
		self.current_data = None
		self.current_filtered_data = None
		self.current_filter = None
		try:
			file_handle = open(file_name, 'r')
			csv_obj = csv.reader(file_handle)
			self.current_data = [row for row in csv_obj]
			file_handle.close()
		except:
			msg = 'Cannot open file '+file_name
			raise IOError(msg)
		self.current_header = [col.upper() for col in self.current_data[0]]
		self.current_data = [[float(col) for col in row] for row in self.current_data[1:]]
		self.current_filtered_data = self.current_data

	def set_filter(self, current_filter):
		"""
		Filter data
		"""
		if isinstance(current_filter, dict) is False:
			msg = 'current_filter must be a dictionary'
			raise TypeError(msg)
		self.current_filtered_data = list()
		for row in self.current_data:
			add = True
			for key in current_filter:
				if key.upper() not in self.current_header:
					msg = key+' not in CSV file header'
					raise RuntimeError(msg)
				col_num = self.current_header.index(key.upper())
				add = True if (row[col_num] == current_filter[key]) and add is True else False
			if add is True:
				self.current_filtered_data.append(row)
		self.current_filter = current_filter

	def add_filter(self, current_filter):
		"""
		Add to current filter
		"""
		if isinstance(current_filter, dict) is False:
			msg = 'current_filter must be a dictionary'
			raise TypeError(msg)
		current_filter = dict(self.current_filter.items() + current_filter.items())
		self.set_filter(current_filter)

	def get_filter(self):
		"""
		Query the currently applied filter
		"""
		return self.current_filter

	def header(self):
		"""
		Return header
		"""
		return self.current_header

	def data(self, col=None):
		"""
		Return data
		"""
		return self.current_data if col is None else self.core_data(self.data, col)

	def filtered_data(self, col=None):
		"""
		Return filtered data
		"""
		return self.current_filtered_data if col is None else self.core_data(self.filtered_data, col)

	def core_data(self, data_pointer, col=None):
		"""
		Slide and return data
		"""
		if isinstance(col, str) is True:
			col = col.upper()
			if col not in self.header():
				msg = col+' not in CSV file header'
				raise RuntimeError(msg)
			col_num = self.header().index(col)
			return [row[col_num] for row in data_pointer()]
		elif isinstance(col, list) is True:
			col_list = col[:]
			for col in col_list:
				if isinstance(col, str) is False:
					msg = 'col must be a list of strings'
					raise TypeError(msg)
				if col.upper() not in self.header():
					msg = col.upper()+' not in CSV file header'
					raise RuntimeError(msg)
			col_index_list = [self.header().index(col.upper()) for col in col_list]
			return [[row[index] for index in col_index_list] for row in data_pointer()]
		else:
			msg = 'Invalid column(s) type'
			raise TypeError(msg)

TETO = CsvFile('data/tx_lut_lckt.csv')
TETO.set_filter({'pvt_corner':0})
TETO.add_filter({'drv_iden_start':17})
print TETO.header()
print TETO.filtered_data(['vo_se','predrv0_ibop'])

