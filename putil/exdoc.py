# exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import copy

import putil.exh
import putil.misc
import putil.tree


###
# Context manager
###
class ExDocCxt(object):	#pylint: disable=R0903
	""" Context manager to simplify exception tracing. For example:

		>>> with putil.exdoc.ExDocCxt() as exdoc_obj:
		...     test_module()
		>>> exdoc_obj.get_sphinx_doc('my_func')

	"""

	def __init__(self, _no_print=True):
		putil.exh.get_or_create_exh_obj(True)
		self._exdoc_obj = putil.exdoc.ExDoc(exh_obj=putil.exh.get_exh_obj(), _empty=True, _no_print=_no_print)

	def __enter__(self):
		return self._exdoc_obj

	def __exit__(self, exc_type, exc_value, exc_tb):
		if exc_type is not None:
			putil.exh.del_exh_obj()
			return False
		self._exdoc_obj._exh_obj = copy.copy(putil.exh.get_exh_obj())	#pylint: disable=W0212
		putil.exh.del_exh_obj()
		self._exdoc_obj._build_ex_tree()	#pylint: disable=W0212


###
# Classes
###
class ExDoc(object):	#pylint: disable=R0902,R0903
	"""
	Generates exception documentation with `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	exh_obj: Exception handler containing exception information for the callable(s) to be documented
	:type	exh_obj: :py:class:`putil.exh.ExHandle` object
	:param	depth: Default hierarchy levels to include in the exceptions per callable
	:type	depth: non-negative integer
	:param	exclude: Default list of (potentially partial) module and callable names to exclude from exceptions per callable (see :py:attr:`putil.exdoc.ExDoc.exclude`)
	:type	exclude: list
	:rtype: :py:class:`putil.exdoc.ExDoc()` object
	:raises:
	 * TypeError (Argument `depth` is not valid)

	 * TypeError (Argument `exclude` is not valid)

	 * TypeError (Argument `exh_obj` is not valid)

	 * ValueError (Object of argument `exh_obj` does not have any exception trace information)
	"""
	def __init__(self, exh_obj, depth=None, exclude=None, _empty=False, _no_print=False):
		if (not _empty) and (not isinstance(exh_obj, putil.exh.ExHandle)):
			raise TypeError('Argument `exh_obj` is not valid')
		if (not _empty) and (not exh_obj.exceptions_db):
			raise ValueError('Object of argument `exh_obj` does not have any exception trace information')
		if not isinstance(_no_print, bool):
			raise TypeError('Argument `_no_print` is not valid')
		self._exh_obj = exh_obj
		self._no_print = _no_print
		self._depth, self._exclude, self._tobj = 3*[None]
		self._set_depth(depth)
		self._set_exclude(exclude)
		if not _empty:
			self._build_ex_tree()

	def __copy__(self):
		cobj = ExDoc(exh_obj=None, depth=self.depth, exclude=self.exclude[:] if self.exclude else self.exclude, _empty=True, _no_print=self._no_print)
		cobj._exh_obj = copy.copy(self._exh_obj)	#pylint: disable=W0212
		cobj._tobj = copy.copy(self._tobj)	#pylint: disable=W0212
		return cobj

	def _build_ex_tree(self):
		""" Construct exception tree from trace """
		# Load exception data into tree structure
		cdb = self._exh_obj.callables_db
		sep = self._exh_obj.callables_separator
		data = self._exh_obj.exceptions_db
		unique_data = []
		for ditem in data:
			# Detect setter/getter/deleter functions of properties and re-name them, faster to do it before tree is built
			#ditem['name'] = sep.join(['{0}[{1}]'.format(cdb[token]['link'][0]['prop'], cdb[token]['link'][0]['action']) if cdb[token]['link'] else token for token in ditem['name'].split(sep)])
			new_name_list = []
			for token in ditem['name'].split(sep):
				if cdb[token]['link'] and (len(cdb[token]['link']) > 1):
					raise RuntimeError('Functions performing actions for multiple properties not supported')
				elif cdb[token]['link']:
					new_name_list.append('{0}[{1}]'.format(cdb[token]['link'][0]['prop'], cdb[token]['link'][0]['action']))
				else:
					new_name_list.append(token)
			ditem['name'] = sep.join(new_name_list)
			unique_data.append(ditem)
		# Actually build tree
		self._tobj = putil.tree.Tree(sep)
		try:
			self._tobj.add_nodes(unique_data)
		except ValueError as eobj:
			if str(eobj).startswith('Illegal node name'):
				raise RuntimeError('Exceptions do not have a common callable')
			raise
		except:
			raise
		# Find closest root node to first branching
		node = self._tobj.root_name
		while len(self._tobj.get_children(node)) == 1:
			node = self._tobj.get_children(node)[0]
		if not self._tobj.is_root(node):
			self._tobj.make_root(node)
			self._tobj.delete_prefix(self._tobj.node_separator.join(node.split(self._tobj.node_separator)[:-1]))
		self._print_ex_tree()

	def _get_depth(self):
		""" depth getter """
		return self._depth

	def _get_exclude(self):
		""" exclude getter """
		return self._exclude

	def _print_ex_tree(self):
		""" Prints exception tree """
		if not self._no_print:
			print str(self._tobj)

	def _set_depth(self, depth):
		""" depth setter """
		if depth and ((not isinstance(depth, int)) or (isinstance(depth, int) and (depth < 0))):
			raise TypeError('Argument `depth` is not valid')
		self._depth = depth

	def _set_exclude(self, exclude):
		""" exclude setter """
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise TypeError('Argument `exclude` is not valid')
		self._exclude = exclude

	def get_sphinx_doc(self, name, depth=None, exclude=None):	#pylint: disable=R0912,R0914,R0915
		"""
		Returns exception list marked up in `reStructuredText`_

		:param	name: Name of the callable (method or function) to generate exception documentatio for
		:type	name: string
		:param	depth: Hierarchy levels to include in the exceptions list (overrides default **depth** argument)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and callable names to exclude from exceptions list  (overrides default **exclude** argument)
		:type	exclude: list
		:raises:
		 * RuntimeError (Callable not found in exception list: *[name]*)

		 * TypeError (Argument `depth` is not valid)

		 * TypeError (Argument `exclude` is not valid)
		"""
		if depth and ((not isinstance(depth, int)) or (isinstance(depth, int) and (depth < 0))):
			raise TypeError('Argument `depth` is not valid')
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise TypeError('Argument `exclude` is not valid')
		depth = self._depth if depth == None else depth
		exclude = self._exclude if not exclude else exclude
		callable_dict = {}
		prop = False
		# Try to find "regular" callable
		try:
			callable_dict[self._tobj.search_tree(name)[0]] = {'type':'regular'}
		except:	#pylint: disable=W0702
			# Try to find property callable
			for action in ['fget', 'fset', 'fdel']:
				prop_name = '{0}[{1}]'.format(name, action)
				try:
					callable_dict[self._tobj.search_tree(prop_name)[0]] = {'type':action}
					prop = True
				except:	#pylint: disable=W0702
					pass
		if not callable_dict:
			raise RuntimeError('Callable not found in exception list: {0}'.format(name))
		# Create exception table taking into account depth and exclude arguments
		sep = self._tobj.node_separator
		for callable_root in callable_dict:
			exlist = []
			root_hierarchy_level = callable_root.count(sep)
			for full_node, rebased_node in [(node, sep.join(node.split(sep)[root_hierarchy_level:])) for node in self._tobj.get_subtree(callable_root)]:	#pylint: disable=W0212
				data = self._tobj._get_data(full_node)	#pylint: disable=W0212
				if ((depth == None) or ((depth != None) and (rebased_node.count(sep) <= depth))) and ((not exclude) or (not any([item in rebased_node for item in exclude]))) and data:
					for exc in data:
						exlist.append(exc)
			callable_dict[callable_root]['exlist'] = exlist[:]
		# Generate final output
		if prop:
			if len(callable_dict) == 1:
				callable_root = callable_dict.keys()[0]
				action = callable_dict[callable_root]['type']
				desc = 'retrieved' if action == 'fget' else ('assigned' if action == 'fset' else 'deleted')
				exlist = sorted(list(set(callable_dict[callable_root]['exlist'])))
				exoutput = [':raises: (when {0}) {1}'.format(desc, exlist[0])] if len(exlist) == 1 else [':raises: (when {0})'.format(desc)]+[' * {0}\n'.format(exname) for exname in exlist]
			else:
				exoutput = [':raises:']
				for action in ['fset', 'fdel', 'fget']:
					desc = 'retrieved' if action == 'fget' else ('assigned' if action == 'fset' else 'deleted')
					for callable_root in callable_dict:
						if callable_dict[callable_root]['type'] == action:
							exlist = sorted(list(set(callable_dict[callable_root]['exlist'])))
							exoutput = exoutput+[' * When {0}\n'.format(desc)]+['   * {0}\n'.format(exname) for exname in exlist]
		else:
			exlist = sorted(list(set(callable_dict[callable_dict.keys()[0]]['exlist'])))
			exoutput = [':raises: {0}'.format(exlist[0])] if len(exlist) == 1 else [':raises:']+[' * {0}\n'.format(exname) for exname in exlist]
		return ('\n'.join(exoutput)).rstrip() if exoutput else ''

	depth = property(_get_depth, _set_depth, None, doc='Call hierarchy depth')
	"""
	Default hierarchy levels to include in the exceptions per callable

	:rtype: non-negative integer
	:raises: TypeError (Argument `depth` is not valid)
	"""	#pylint: disable=W0105

	exclude = property(_get_exclude, _set_exclude, None, doc='Modules and callables to exclude')
	"""
	Default list of (potentially partial) module and callable names to exclude from exceptions per callable. For example, :code:`['putil.ex']` excludes all exceptions from modules :code:`putil.exh` and :code:`putil.exdoc`.
	In addition to these modules, :code:`['putil.ex', 'putil.eng.peng']` excludes exceptions from the function :code:`putil.eng.peng`.

	:rtype: list
	:raises: TypeError (Argument `exclude` is not valid)
	"""	#pylint: disable=W0105
