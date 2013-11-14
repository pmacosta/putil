"""
Unit testing for util_logging
"""
import unittest

import util_logging

class TestUtilLogging(unittest.TestCase):	#pylint: disable-msg=R0904
	"""
	unittest class to verify correct implementation of the logging utility methods
	"""

	def test_logger_wrong_type(self):	#pylint: disable-msg=C0103
		"""
		Test correct type of logger object if passed
		"""
		self.assertRaisesRegexp(TypeError, r'logger must be a logger object', util_logging.Plogger, None, 12345)

	def test_name_wrong_type(self):	#pylint: disable-msg=C0103
		"""
		Test correct type of name if passed
		"""
		self.assertRaisesRegexp(TypeError, r'name must be a string', util_logging.Plogger, 12345)

	def test_log_level_type(self):	#pylint: disable-msg=C0103
		"""
		Test correct type of log_level if passed
		"""
		self.assertRaisesRegexp(TypeError, r'log_level must be an integer or a string', util_logging.Plogger, __name__, None, 1+3j)

	def test_log_level_wrong_int(self):	#pylint: disable-msg=C0103
		"""
		Test correct integer value of log_level if passed
		"""
		self.assertRaisesRegexp(ValueError, r'log_level must be an integer in \[10, 20, 30, 40, 50, 60\]', util_logging.Plogger, __name__, None, -35)

	def test_log_level_wrong_str(self):	#pylint: disable-msg=C0103
		"""
		Test correct string value of log_level if passed
		"""
		self.assertRaisesRegexp(ValueError, r'log_level must be an integer in \[DEBUG, INFO, WARNING, ERROR, CRITICAL, NONE\]', util_logging.Plogger, __name__, None, 'a')

	def test_log_file_type(self):	#pylint: disable-msg=C0103
		"""
		Test correct type of log_file if passed
		"""
		self.assertRaisesRegexp(TypeError, r'log_file must be a string', util_logging.Plogger, __name__, None, 60, 3)

	def test_log_file_cannot_be_opened(self):	#pylint: disable-msg=C0103
		"""
		Test correct type of log_file if passed
		"""
		self.assertRaisesRegexp(IOError, r'log_file cannot be opened', util_logging.Plogger, __name__, None, 60, './nodir/test.log')

	def test_log_level_int_works(self):	#pylint: disable-msg=C0103
		"""
		Test that log_level() method correctly modifies logging level (log level specified as an integer)
		"""
		test_logger = util_logging.Plogger('tlog1', None, 'DEBUG')
		result = True if test_logger.log_level_int() == test_logger.logger().getEffectiveLevel() else False
		for level in range(10, 70, 10):
			test_logger.log_level(level)
			result = True if test_logger.log_level_int() == test_logger.logger().getEffectiveLevel() else False
			if result is False:
				break
		self.assertTrue(result)

	def test_log_level_str_works(self):	#pylint: disable-msg=C0103
		"""
		Test that log_level() method correctly modifies logging level (log level specified as a string)
		"""
		test_logger = util_logging.Plogger('tlog1', None, 'debug')
		result = True if test_logger.log_level == 'DEBUG' else False
		level_int_list = range(10, 70, 10)
		level_str_list = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NONE']
		for level in level_str_list:
			test_logger.log_level(level)
			result = True if test_logger.log_level() == level_str_list[level_int_list.index(test_logger.logger().getEffectiveLevel())] else False
			if result is False:
				break
		self.assertTrue(result)

	def test_name_works(self):	#pylint: disable-msg=C0103
		"""
		Test that name() method correctly modifies logger name 
		"""
		test_logger = util_logging.Plogger('tlog1', None, 'debug')
		new_name = 'tlog999'
		test_logger.name(new_name)
		result = True if (test_logger.name() == new_name) and (test_logger.logger().name == new_name) else False
		self.assertTrue(result)

	def test_log_file_works(self):	#pylint: disable-msg=C0103
		"""
		Test that log_file() method correctly modifies logging file 
		"""
		test_logger = util_logging.Plogger('tlog1', None, 'debug')
		new_file_name = 'test.log'
		print
		print new_file_name
		test_logger.log_file(new_file_name)
		print new_file_name
		result = True if (test_logger.log_file() == new_file_name) and (util_logging._find_logger_basefilename(test_logger.logger()) == new_file_name) else False	#pylint: disable-msg=W0212
		#print new_file_name
		print test_logger.log_file()
		print util_logging._find_logger_basefilename(test_logger.logger())
		self.assertTrue(result)

if __name__ == '__main__':
	unittest.main(verbosity=2)
