"""
Unit testing for util_dict
"""
import unittest

import util_dict

class TestUtilDict(unittest.TestCase):	#pylint: disable-msg=R0904
	"""
	unittest class to verify correct implementation of the dictionary utility methods
	"""

	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_cidict_positional_argument_null_keyword_arguments_null(self):	#pylint: disable-msg=C0103
		"""
		If no positional argument is given, an empty dictionary is created.
		"""
		test_dict = util_dict.CiDict()
		self.assertEqual({}, test_dict)

	def test_cidict_positional_argument_dict_null_keyword_arguments_null1(self):	#pylint: disable-msg=C0103
		"""
		If a positional argument is given and it is a mapping object, a dictionary is created with the same key-value pairs as the mapping object.
		"""
		test_dict = util_dict.CiDict({'FiRsT':1, 'SECOND':2})
		self.assertEqual({'first':1, 'second':2}, test_dict)

	def test_cidict_positional_argument_dict_null_keyword_arguments_null2(self):	#pylint: disable-msg=C0103
		"""
		If a positional argument is given and it is a mapping object, a dictionary is created with the same key-value pairs as the mapping object.
		"""
		test_dict = util_dict.CiDict({'FiRsT':1, 'SECOND':2, 7:6})
		self.assertEqual({'first':1, 'second':2, 7:6}, test_dict)

	def test_cidict_positional_argument_dict_null_keyword_arguments_null3(self):	#pylint: disable-msg=C0103
		"""
		If a positional argument is given and it is a mapping object, a dictionary is created with the same key-value pairs as the mapping object.
		"""
		test_dict = util_dict.CiDict({'Xb'})
		self.assertEqual({'x':'b'}, test_dict)

	def test_cidict_positional_argument_zip_keyword_arguments_null(self):	#pylint: disable-msg=C0103
		"""
		Otherwise, the positional argument must be an iterator object. Each item in the iterable must itself be an iterator with exactly two objects.
		The first object of each item becomes a key in the new dictionary, and the second object the corresponding value. If a key occurs more than once,
		the last value for that key becomes the corresponding value in the new dictionary.
		"""
		test_dict = util_dict.CiDict(zip(['FiRsT', 'SECOND'], [1,  2]))
		self.assertEqual({'first':1, 'second':2}, test_dict)

	def test_cidict_positional_argument_list_keyword_arguments_null(self):	#pylint: disable-msg=C0103
		"""
		Otherwise, the positional argument must be an iterator object. Each item in the iterable must itself be an iterator with exactly two objects.
		The first object of each item becomes a key in the new dictionary, and the second object the corresponding value. If a key occurs more than once,
		the last value for that key becomes the corresponding value in the new dictionary.
		"""
		test_dict = util_dict.CiDict([('FiRsT', 1), ('SECOND', 2)])
		self.assertEqual({'first':1, 'second':2}, test_dict)

	def test_cidict_positional_argument_null_keyword_arguments_not_null(self):	#pylint: disable-msg=C0103
		"""
		If no positional argument is given, an empty dictionary is created.
		If keyword arguments are given, the keyword arguments and their values are added to the dictionary created from the positional argument.
		If a key being added is already present, the value from the keyword argument replaces the value from the positional argument.
		"""
		test_dict = util_dict.CiDict(FiRsT=1, SECOND=2)
		self.assertEqual({'first':1, 'second':2}, test_dict)

	def test_cidict_positional_argument_dict_null_keyword_arguments_not_null(self):	#pylint: disable-msg=C0103
		"""
		If a positional argument is given and it is a mapping object, a dictionary is created with the same key-value pairs as the mapping object.
		If keyword arguments are given, the keyword arguments and their values are added to the dictionary created from the positional argument.
		If a key being added is already present, the value from the keyword argument replaces the value from the positional argument.
		"""
		test_dict = util_dict.CiDict({'FiRsT':1, 'SECOND':2}, Third=3, sEcOnD=4)
		self.assertEqual({'first':1, 'second':4, 'third':3}, test_dict)

	def test_cidict_positional_argument_zip_keyword_arguments_not_null(self):	#pylint: disable-msg=C0103
		"""
		Otherwise, the positional argument must be an iterator object. Each item in the iterable must itself be an iterator with exactly two objects.
		The first object of each item becomes a key in the new dictionary, and the second object the corresponding value. If a key occurs more than once,
		the last value for that key becomes the corresponding value in the new dictionary.
		If keyword arguments are given, the keyword arguments and their values are added to the dictionary created from the positional argument.
		If a key being added is already present, the value from the keyword argument replaces the value from the positional argument.
		"""
		test_dict = util_dict.CiDict(zip(['FiRsT', 'SECOND'], [1,  2]), Third=3, sEcOnD=4)
		self.assertEqual({'first':1, 'second':4, 'third':3}, test_dict)

	def test_cidict_positional_argument_list_keyword_arguments_not_null(self):	#pylint: disable-msg=C0103
		"""
		Otherwise, the positional argument must be an iterator object. Each item in the iterable must itself be an iterator with exactly two objects.
		The first object of each item becomes a key in the new dictionary, and the second object the corresponding value. If a key occurs more than once,
		the last value for that key becomes the corresponding value in the new dictionary.
		If keyword arguments are given, the keyword arguments and their values are added to the dictionary created from the positional argument.
		If a key being added is already present, the value from the keyword argument replaces the value from the positional argument.
		"""
		test_dict = util_dict.CiDict([('FiRsT', 1), ('SECOND', 2)], Third=3, sEcOnD=4)
		self.assertEqual({'first':1, 'second':4, 'third':3}, test_dict)

	def test_cidict_positiional_argument_malformed_dict1(self):	#pylint: disable-msg=C0103
		"""
		Test if case-insensitive dictionary class raises same exception when a malformed dictionary is given to its constructor
		"""
		self.assertRaisesRegexp(ValueError, 'dictionary update sequence element #0 has length 5; 2 is required', util_dict.CiDict, {'hello'})

	def test_cidict_positiional_argument_malformed_list(self):	#pylint: disable-msg=C0103
		"""
		Test if case-insensitive dictionary class raises same exception when a malformed dictionary is given to its constructor
		"""
		self.assertRaisesRegexp(TypeError, 'cannot convert dictionary update sequence element #1 to a sequence', util_dict.CiDict, [(1, 2), (1), (2)])

	def test_cidict_get_item1(self):
		"""
		Test that an item can be retrieved in case-insensitive manner
		"""
		test_dict = util_dict.CiDict([('FiRsT', 1), ('SECOND', 2)], Third=3, sEcOnD=4)
		self.assertEqual(4, test_dict['SeCoNd'])

	def test_cidict_get_item2(self):
		"""
		Test that an item can be retrieved in case-insensitive manner
		"""
		test_dict = util_dict.CiDict([('FiRsT', 1), ('SECOND', 2)], Third=3, sEcOnD=4)
		self.assertEqual(4, test_dict['second'])

	def test_cidict_set_item1(self):
		"""
		Test that an item can be retrieved in case-insensitive manner
		"""
		test_dict = util_dict.CiDict([('FiRsT', 1), ('SECOND', 2)], Third=3, sEcOnD=4)
		test_dict['FouRTH'] = 'Hello, world'
		self.assertEqual('Hello, world', test_dict['fourth'])


if __name__ == '__main__':
	unittest.main(verbosity=2)
