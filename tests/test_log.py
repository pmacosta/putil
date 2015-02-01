# test_log.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

"""
Unit testing for putil.logging
"""

import os
import unittest

import putil.logging

class TestUtilLogging(unittest.TestCase):	#pylint: disable=R0904
	"""
	unittest class to verify correct implementation of the logging utility methods
	"""

	def test_logger_wrong_type(self):	#pylint: disable=C0103
		"""
		Test correct type of logger object if passed
		"""
		self.assertRaisesRegexp(TypeError, r'logger must be a logger object', putil.logging._Plogger, None, 12345)	#pylint: disable=W0212

	def test_name_wrong_type(self):	#pylint: disable=C0103
		"""
		Test correct type of name if passed
		"""
		self.assertRaisesRegexp(TypeError, r'name must be a string', putil.logging._Plogger, 12345)	#pylint: disable=W0212

	def test_log_level_type(self):	#pylint: disable=C0103
		"""
		Test correct type of log_level if passed
		"""
		self.assertRaisesRegexp(TypeError, r'log_level must be an integer or a string', putil.logging._Plogger, __name__, None, 1+3j)	#pylint: disable=W0212

	def test_log_level_wrong_int(self):	#pylint: disable=C0103
		"""
		Test correct integer value of log_level if passed
		"""
		self.assertRaisesRegexp(ValueError, r'log_level must be an integer in \[10, 20, 30, 40, 50, 60\]', putil.logging._Plogger, __name__, None, -35)	#pylint: disable=W0212

	def test_log_level_wrong_str(self):	#pylint: disable=C0103
		"""
		Test correct string value of log_level if passed
		"""
		self.assertRaisesRegexp(ValueError, r'log_level must be an integer in \[DEBUG, INFO, WARNING, ERROR, CRITICAL, NONE\]', putil.logging._Plogger, __name__, None, 'a')	#pylint: disable=W0212

	def test_log_file_type(self):	#pylint: disable=C0103
		"""
		Test correct type of log_file if passed
		"""
		self.assertRaisesRegexp(TypeError, r'log_file must be a string', putil.logging._Plogger, __name__, None, 60, 3)	#pylint: disable=W0212

	def test_log_file_cannot_be_opened(self):	#pylint: disable=C0103
		"""
		Test correct type of log_file if passed
		"""
		self.assertRaisesRegexp(IOError, r'log_file cannot be opened', putil.logging._Plogger, __name__, None, 60, './nodir/test.log')	#pylint: disable=W0212

	def test_log_level_int_works(self):	#pylint: disable=C0103
		"""
		Test that log_level() method correctly modifies logging level (log level specified as an integer)
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'DEBUG')	#pylint: disable=W0212
		result = True if test_logger.log_level_int() == test_logger.logger().getEffectiveLevel() else False
		for level in range(10, 70, 10):
			test_logger.log_level(level)
			result = True if test_logger.log_level_int() == test_logger.logger().getEffectiveLevel() else False
			if result is False:
				break
		self.assertTrue(result)

	def test_log_level_str_works(self):	#pylint: disable=C0103
		"""
		Test that log_level() method correctly modifies logging level (log level specified as a string)
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'debug')	#pylint: disable=W0212
		result = True if test_logger.log_level == 'DEBUG' else False
		level_int_list = range(10, 70, 10)
		level_str_list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NONE']
		for level in level_str_list:
			test_logger.log_level(level)
			result = True if test_logger.log_level() == level_str_list[level_int_list.index(test_logger.logger().getEffectiveLevel())] else False
			if result is False:
				break
		self.assertTrue(result)

	def test_name_works(self):	#pylint: disable=C0103
		"""
		Test that name() method correctly modifies logger name
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'debug')	#pylint: disable=W0212
		new_name = 'tlog999'
		test_logger.name(new_name)
		result = True if (test_logger.name() == new_name) and (test_logger.logger().name == new_name) else False
		self.assertTrue(result)

	def test_log_file_works(self):	#pylint: disable=C0103
		"""
		Test that log_file() method correctly modifies logging file
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'debug')	#pylint: disable=W0212
		new_file_name = 'test.log'
		test_logger.log_file(new_file_name)
		result = True if (test_logger.log_file() == os.path.abspath(new_file_name)) and (putil.logging._find_logger_basefilename(test_logger.logger()) == os.path.abspath(new_file_name)) else False	#pylint: disable=W0212
		self.assertTrue(result)

	def test_str_works(self):
		"""
		Test that str() method produces the correct output
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'debug')	#pylint: disable=W0212
		ret = 'Logger configuration\nName.....: tlog999\nLog level: DEBUG\nLog file.: sys.stdout'
		self.assertEqual(ret, str(test_logger))

	def test_repr_works(self):
		"""
		Test that repr() method produces the correct output
		"""
		test_logger = putil.logging._Plogger('tlog1', None, 'debug')	#pylint: disable=W0212
		ret = 'Logger configuration\nName.....: tlog999\nLog level: DEBUG\nLog file.: sys.stdout'
		self.assertEqual(ret, repr(test_logger))

	def test_logger_works(self):
		"""
		Test that logger() method correctly initializes internal structure
		"""
		log_file = './test.log'
		test_logger1 = putil.logging._Plogger('tlog1', None, 'INFO', log_file)	#pylint: disable=W0212
		test_logger2 = putil.logging._Plogger('tlog2', None, 'debug')	#pylint: disable=W0212
		ret_before = 'Logger configuration\nName.....: tlog2\nLog level: DEBUG\nLog file.: sys.stdout'
		result = True if str(test_logger2) == ret_before else False
		if result is True:
			test_logger2.logger(test_logger1.logger())
			ret_after = 'Logger configuration\nName.....: tlog1\nLog level: INFO\nLog file.: '+os.path.abspath(log_file)
			result = True if str(test_logger2) == ret_after else False
		self.assertTrue(result)

	def test_copy_works(self):
		"""
		Test copy() methods produces an identical copy
		"""
		log_file = './test.log'
		test_logger1 = putil.logging._Plogger('tlog1', None, 'INFO', log_file)	#pylint: disable=W0212
		test_logger2 = test_logger1.copy()
		self.assertEqual(str(test_logger1), str(test_logger2))


if __name__ == '__main__':
	unittest.main(verbosity=2)
