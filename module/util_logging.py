# util_logging.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Logging-related utility classes, methods, functions and constants
"""

import os
import sys
import logging

# StackOverflow question: http://stackoverflow.com/questions/3311255/how-to-get-file-the-python-logging-module-is-currently-logging-to
def _find_logger_basefilename(logger):
	"""
	Finds the logger base filename(s) currently there is only one
	"""
	log_file = None
	parent = logger.__dict__['parent']
	if parent.__class__.__name__ == 'RootLogger':
		# this is where the file name lives
		for logger_handle in logger.__dict__['handlers']:
			if logger_handle.__class__.__name__ == 'FileHandler':
				log_file = logger_handle.baseFilename
			if logger_handle.__class__.__name__ == 'StreamHandler':
				log_file = 'sys.stdout'
	else:
		log_file = _find_logger_basefilename(parent)
	return log_file


def _setup_logging(name, log_level, log_file):
	"""
	Setup generic logging functionality
	"""
	logger = logging.getLogger(name)
	logger.setLevel(getattr(logging, log_level.upper()) if log_level.upper() != 'NONE' else 60) # CRITICAL (50),ERROR (40),WARNING (30),INFO (20),DEBUG (10),NOTSET (0)
	handler = logging.StreamHandler(sys.stdout) if (log_file is None) or (logger.getEffectiveLevel() == 60) else logging.FileHandler(log_file,'w')
	handler.setLevel(getattr(logging, log_level.upper()) if log_level.upper() != 'NONE' else 60)
	handler.setFormatter(logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(message)s'))
	logger.addHandler(handler)
	return logger


class _Plogger(object):
	"""
	Creates or modifies logger. If logger is done log_level and log_file arguments are ignored
	"""
	def __init__(self, name=None, logger=None, log_level=60, log_file=None):
		self.level_int_list = range(10, 70, 10)
		self.level_str_list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NONE']
		self.current_name = None
		self.current_log_level = None
		self.current_log_file = None
		self.current_logger = None
		self.name(__name__ if name is None else name)
		self.log_level(log_level if logger is None else logger.getEffectiveLevel() if isinstance(logger, logging.Logger) is True else None)
		self.log_file(log_file if logger is None else _find_logger_basefilename(logger) if isinstance(logger, logging.Logger) is True else None)	#pylint: disable-msg=W0212
		self.logger(logger if logger is not None else _setup_logging(name, self.log_level(), self.log_file()))	#pylint: disable-msg=W0212

	def name(self, name=None):
		"""
		Sets or returns logger name
		"""
		if name is None:
			return self.current_name
		else:
			if isinstance(name, str) is False:
				msg = 'name must be a string'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger(msg)
				raise TypeError(msg)
			self.current_name = name
			if isinstance(self.current_logger, logging.Logger) is True:
				self.current_logger.name = self.current_name


	def logger(self, logger=None):
		"""
		Sets or returns logger object
		"""
		if logger is None:
			return self.current_logger
		else:
			if isinstance(logger, logging.Logger) is False:
				msg = 'logger must be a logger object'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger(msg)
				raise TypeError(msg)
			self.current_logger = logger
			self.current_log_level = self.level_str_list[self.level_int_list.index(self.current_logger.getEffectiveLevel())]
			self.current_log_file = _find_logger_basefilename(self.current_logger)	#pylint: disable-msg=W0212
			self.current_name = self.current_logger.name

	def log_level(self, log_level=None):
		"""
		Sets or returns log level
		"""
		if log_level is None:
			return self.current_log_level
		else:
			log_level = log_level.upper() if isinstance(log_level, str) is True else log_level
			if (isinstance(log_level, int) is False) and (isinstance(log_level, str) is False):
				msg = 'log_level must be an integer or a string'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger.error(msg)
				raise TypeError(msg)
			if (isinstance(log_level, int) is True) and (log_level not in self.level_int_list):
				msg = 'log_level must be an integer in ['+', '.join([str(level_int) for level_int in self.level_int_list])+']'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger.error(msg)
				raise ValueError(msg)
			if (isinstance(log_level, str) is True) and (log_level not in self.level_str_list):
				msg = 'log_level must be an integer in ['+', '.join(self.level_str_list)+']'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger.error(msg)
				raise ValueError(msg)
			self.current_log_level = log_level if isinstance(log_level, str) is True else self.level_str_list[self.level_int_list.index(log_level)]
			if isinstance(self.current_logger, logging.Logger) is True:
				self.current_logger.setLevel(self.level_int_list[self.level_str_list.index(self.current_log_level)])

	def log_level_int(self):
		"""
		Returns log level in numeric format
		"""
		return self.level_int_list[self.level_str_list.index(self.current_log_level)]

	def log_file(self, log_file=None):
		"""
		Sets or returns log file
		"""
		if log_file is None:
			return self.current_log_file
		else:
			if isinstance(log_file, str) is False:
				msg = 'log_file must be a string'
				if isinstance(self.current_logger, logging.Logger) is True:
					self.current_logger.error(msg)
				raise TypeError(msg)
			if os.path.isfile(log_file) is False:
				try:
					file_handle = open(log_file, 'a')
					file_handle.close()
					os.remove(log_file)
				except:
					msg = 'log_file cannot be opened'
					if isinstance(self.current_logger, logging.Logger) is True:
						self.current_logger.error(msg)
					raise IOError(msg)
			self.current_log_file = log_file
			# Change log file maintaining current log level and format
			if isinstance(self.current_logger, logging.Logger) is True:
				current_format = self.current_logger.handlers[0].formatter._fmt	#pylint: disable-msg=W0212
				current_level = self.log_level_int()
				if _find_logger_basefilename(self.current_logger) != 'sys.stdout':
					self.current_logger.handlers[0].stream.close()
				self.current_logger.removeHandler(self.current_logger.handlers[0])
				file_handler = logging.FileHandler(log_file)
				file_handler.setLevel(current_level)
				formatter = logging.Formatter(current_format)
				file_handler.setFormatter(formatter)
				self.current_logger.addHandler(file_handler)
				self.current_log_file = _find_logger_basefilename(self.current_logger)

	def __str__(self):
		"""
		Prints configuration nicely formatted
		"""
		ret = 'Logger configuration'+'\n'
		ret += 'Name.....: '+self.name()+'\n'
		ret += 'Log level: '+self.log_level()+'\n'
		ret += 'Log file.: '+self.log_file()
		return ret

	def __repr__(self):
		"""
		Retuns object id
		"""
		return self.__str__()

	def copy(self):
		"""
		Creates a copy of the current logger
		"""
		return _Plogger(logger=self.logger())
