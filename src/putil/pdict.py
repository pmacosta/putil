# pdict.py
# Copyright (c) 2014 Pablo Acosta-Serafini
# See LICENSE for details

"""
Dictionary-related utility classes, methods, functions and constants
"""

class CiDict(dict):
	"""
	Dictionary class with case-insensitive keys
	"""
	def __init__(self, posarg=None, **kwargs):
		# Algorithm:
		# 1. Create a dictionary with the build-in dict() method (this ensures that all exceptions will be identical)
		# 2. Create a new dictionary with lower-case keys of dictionary created in step #1
		# 3. Associate dictionary created in step #2 to self
		# Method may not be the most efficient for large dictionaries, where an iteration-based algorithm may have less memory requirements
		_dict1 = dict()
		if posarg is not None:
			try:
				_dict1.update(posarg)
			except TypeError:
				raise
			except ValueError:
				raise
		if kwargs is not None:
			try:
				_dict1.update(kwargs)
			except TypeError:
				raise
			except ValueError:
				raise
		_dict2 = dict()
		for key in _dict1.keys():
			_dict2[key.lower() if isinstance(key, str) is True else key] = _dict1[key]
		dict.__init__(self, _dict2)

	def __getitem__(self, key):
		return super(CiDict, self).__getitem__(key.lower() if isinstance(key, str) is True else key)

	def __setitem__(self, key, val):
		super(CiDict, self).__setitem__(key.lower() if isinstance(key, str) is True else key, val)
