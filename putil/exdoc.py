# exdoc.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import bisect, copy, os, sys, textwrap

import putil.exh, putil.misc, putil.tree


###
# Global variables
###
_MINWIDTH = 40	# Minimum width of the output lines, broken out as a global variable mainly to ease testing


###
# Functions
###
def _format_msg(text, width, indent=0):
	""" Replace newline characters \n with ``\n`` and wrap text as needed"""
	text = repr(text).replace('\\n', ' ``\\n`` ').replace('`', '\\`')
	return ('\n'.join(textwrap.wrap(text, width, subsequent_indent=indent*' ')))[1:-1].rstrip()


###
# Context managers
###
class ExDocCxt(object):	#pylint: disable=R0903
	""" Context manager to simplify exception tracing; it sets up the tracing environment and returns a :py:class:`putil.exdoc.ExDoc` object that can the be used in the documentation string of each callable to extract the
	exceptions documentation with either :py:meth:`putil.exdoc.ExDoc.get_sphinx_doc` or :py:meth:`putil.exdoc.ExDoc.get_sphinx_autodoc`. For example:

		>>> with putil.exdoc.ExDocCxt() as exdoc_obj:
		...     test_module()
		>>> exdoc_obj.get_sphinx_doc('my_func')
		.. Auto-generated exceptions documentation for my_func
		:raises: [...]

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
		self._exdoc_obj._build_module_db()	#pylint: disable=W0212


###
# Classes
###
class ExDoc(object):	#pylint: disable=R0902,R0903
	"""
	Generates exception documentation with `reStructuredText <http://docutils.sourceforge.net/rst.html>`_ mark-up

	:param	exh_obj: Exception handler containing exception information for the callable(s) to be documented
	:type	exh_obj: :py:class:`putil.exh.ExHandle` object
	:param	depth: Default hierarchy levels to include in the exceptions per callable (see :py:attr:`putil.exdoc.ExDoc.depth`)
	:type	depth: non-negative integer
	:param	exclude: Default list of (potentially partial) module and callable names to exclude from exceptions per callable (see :py:attr:`putil.exdoc.ExDoc.exclude`)
	:type	exclude: list
	:rtype: :py:class:`putil.exdoc.ExDoc` object
	:raises:
	 * RuntimeError (Argument \\`depth\\` is not valid)

	 * RuntimeError (Argument \\`exclude\\` is not valid)

	 * RuntimeError (Argument \\`exh_obj\\` is not valid)

	 * ValueError (Object of argument \\`exh_obj\\` does not have any exception trace information)
	"""
	def __init__(self, exh_obj, depth=None, exclude=None, _empty=False, _no_print=False):
		if (not _empty) and (not isinstance(exh_obj, putil.exh.ExHandle)):
			raise RuntimeError('Argument `exh_obj` is not valid')
		if (not _empty) and (not exh_obj.exceptions_db):
			raise ValueError('Object of argument `exh_obj` does not have any exception trace information')
		if not isinstance(_no_print, bool):
			raise RuntimeError('Argument `_no_print` is not valid')
		self._module_obj_db = {}
		self._exh_obj = exh_obj
		self._no_print = _no_print
		self._depth, self._exclude, self._tobj = 3*[None]
		self._set_depth(depth)
		self._set_exclude(exclude)
		if not _empty:
			self._build_ex_tree()
			self._build_module_db()

	def __copy__(self):
		cobj = ExDoc(exh_obj=None, depth=self.depth, exclude=self.exclude[:] if self.exclude else self.exclude, _empty=True, _no_print=self._no_print)
		cobj._exh_obj = copy.copy(self._exh_obj)	#pylint: disable=W0212
		cobj._tobj = copy.copy(self._tobj)	#pylint: disable=W0212
		cobj._module_obj_db = copy.deepcopy(self._module_obj_db)	#pylint: disable=W0212
		return cobj

	def _build_ex_tree(self):
		""" Construct exception tree from trace """
		# Load exception data into tree structure
		cdb = self._exh_obj.callables_db
		sep = self._exh_obj.callables_separator
		data = self._exh_obj.exceptions_db
		if not data:
			raise RuntimeError('Exceptions database is empty')
		unique_data = []
		for ditem in data:
			# Detect setter/getter/deleter functions of properties and re-name them, faster to do it before tree is built
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

	def _build_module_db(self):
		""" Build database of module callables sorted by line number """
		tdict = {}
		for callable_name, callable_dict in self._exh_obj.callables_db.iteritems():
			if callable_dict['code_id']:
				file_name, line_no = callable_dict['code_id']
				if file_name not in tdict:
					tdict[file_name] = list()
				tdict[file_name].append({'name':'{0}.__init__'.format(callable_name) if callable_dict['type'] == 'class' else callable_name, 'line':line_no})
		for file_name in tdict.iterkeys():
			self._module_obj_db[file_name] = sorted(tdict[file_name], key=lambda idict: idict['line'])

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
			raise RuntimeError('Argument `depth` is not valid')
		self._depth = depth

	def _set_exclude(self, exclude):
		""" exclude setter """
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise RuntimeError('Argument `exclude` is not valid')
		self._exclude = exclude

	def get_sphinx_autodoc(self, depth=None, exclude=None, width=220, error=False):	#pylint: disable=R0201
		"""
		Returns an exception list marked up in `reStructuredText`_ automatically determining callable name

		:param	depth: Hierarchy levels to include in the exceptions list (overrides default **depth** argument; see :py:attr:`putil.exdoc.ExDoc.depth`)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and callable names to exclude from exceptions list  (overrides default **exclude** argument, see :py:attr:`putil.exdoc.ExDoc.exclude`)
		:type	exclude: list
		:param	width: Maximum width of the lines of text (minimum 40)
		:type	width: integer
		:raises:

		 * RuntimeError (Argument \\`depth\\` is not valid)

		 * RuntimeError (Argument \\`exclude\\` is not valid)

		 * RuntimeError (Argument \\`width\\` is not valid)

		 * RuntimeError (Callable not found in exception list: *[name]*)

		 * RuntimeError (Unable to determine callable name)
		"""
		frame = sys._getframe(1)	#pylint: disable=W0212
		index = frame.f_code.co_filename.rfind('+')
		file_name = os.path.abspath(frame.f_code.co_filename[:index])
		line_num = int(frame.f_code.co_filename[index+1:])
		names = [callable_dict['name'] for callable_dict in self._module_obj_db[file_name]]
		line_nums = [callable_dict['line'] for callable_dict in self._module_obj_db[file_name]]
		name = names[bisect.bisect(line_nums, line_num)-1]
		return self.get_sphinx_doc(name, depth=depth, exclude=exclude, width=width, error=error)

	def get_sphinx_doc(self, name, depth=None, exclude=None, width=230, error=False):	#pylint: disable=R0912,R0913,R0914,R0915
		"""
		Returns an exception list marked up in `reStructuredText`_

		:param	name: Name of the callable (method, function or class property) to generate exceptions documentation for
		:type	name: string
		:param	depth: Hierarchy levels to include in the exceptions list (overrides default **depth** argument; see :py:attr:`putil.exdoc.ExDoc.depth`)
		:type	depth: non-negative integer
		:param	exclude: List of (potentially partial) module and callable names to exclude from exceptions list  (overrides default **exclude** argument; see :py:attr:`putil.exdoc.ExDoc.exclude`)
		:type	exclude: list
		:param	width: Maximum width of the lines of text (minimum 40)
		:type	width: integer
		:raises:
		 * RuntimeError (Argument \\`depth\\` is not valid)

		 * RuntimeError (Argument \\`exclude\\` is not valid)

		 * RuntimeError (Argument \\`width\\` is not valid)

		 * RuntimeError (Callable not found in exception list: *[name]*)
		"""
		if depth and ((not isinstance(depth, int)) or (isinstance(depth, int) and (depth < 0))):
			raise RuntimeError('Argument `depth` is not valid')
		if exclude and ((not isinstance(exclude, list)) or (isinstance(exclude, list) and any([not isinstance(item, str) for item in exclude]))):
			raise RuntimeError('Argument `exclude` is not valid')
		if (not isinstance(width, int)) or (isinstance(width, int) and (width < _MINWIDTH)):
			raise RuntimeError('Argument `width` is not valid')
		depth = self._depth if depth == None else depth
		exclude = self._exclude if not exclude else exclude
		callable_dict = {}
		prop = False
		# Try to find "regular" callable
		# The trace may have several calls to the same callable, capturing potentially different exception or behaviors, thus capture them all
		instances = self._tobj.search_tree(name)
		if instances:
			callable_dict[name] = {'type':'regular', 'instances':instances}
		else:
			# Try to find property callable
			for action in ['fget', 'fset', 'fdel']:
				prop_name = '{0}[{1}]'.format(name, action)
				instances = self._tobj.search_tree(prop_name)
				if instances:
					callable_dict[prop_name] = {'type':action, 'instances':instances}
					prop = True
		if error and (not callable_dict):
			raise RuntimeError('Callable not found in exception list: {0}'.format(name))
		elif not callable_dict:
			return ''
		# Create exception table taking into account depth and exclude arguments
		sep = self._tobj.node_separator
		for name_dict in callable_dict.values():
			exlist = []
			for callable_root in name_dict['instances']:
				root_hierarchy_level = callable_root[:callable_root.index(name)].count(sep)
				for full_node, rebased_node in [(node, sep.join(node.split(sep)[root_hierarchy_level:])) for node in self._tobj.get_subtree(callable_root)]:	#pylint: disable=W0212
					data = self._tobj._get_data(full_node)	#pylint: disable=W0212
					if ((depth == None) or ((depth != None) and (rebased_node.count(sep) <= depth))) and ((not exclude) or (not any([item in rebased_node for item in exclude]))) and data:
						for exc in data:
							exlist.append(exc)
			name_dict['exlist'] = list(set(exlist[:]))
		# Generate final output
		exoutput = [_format_msg('.. Auto-generated exceptions documentation for {0}'.format(name), width)]
		if prop:
			if len(callable_dict) == 1:
				callable_root = callable_dict.keys()[0]
				action = callable_dict[callable_root]['type']
				desc = 'retrieved' if action == 'fget' else ('assigned' if action == 'fset' else 'deleted')
				exlist = sorted(list(set(callable_dict[callable_root]['exlist'])))
				exoutput.extend(['\n{0}'.format(_format_msg(':raises: (when {0}) {1}'.format(desc, exlist[0]), width))] if len(exlist) == 1 else\
					['\n:raises: (when {0})\n'.format(desc)]+[' * {0}\n'.format(_format_msg(exname, width, 3)) for exname in exlist])
			else:
				exoutput.append('\n:raises:')
				for action in ['fset', 'fdel', 'fget']:
					desc = 'retrieved' if action == 'fget' else ('assigned' if action == 'fset' else 'deleted')
					for callable_root in callable_dict:
						if callable_dict[callable_root]['type'] == action:
							exlist = sorted(list(set(callable_dict[callable_root]['exlist'])))
							exoutput.extend([' * When {0}\n'.format(desc)]+['   * {0}\n'.format(_format_msg(exname, width, 5)) for exname in exlist])
		else:
			exlist = sorted(list(set(callable_dict[callable_dict.keys()[0]]['exlist'])))
			exoutput.extend(['\n{0}'.format(_format_msg(':raises: {0}'.format(exlist[0]), width))] if len(exlist) == 1 else ['\n:raises:']+[' * {0}\n'.format(_format_msg(exname, width, 3)) for exname in exlist])
		exoutput[-1] = exoutput[-1].rstrip() + '\n\n'
		return ('\n'.join(exoutput)) if exoutput else ''

	depth = property(_get_depth, _set_depth, None, doc='Call hierarchy depth')
	"""
	Gets or sets the default hierarchy levels to include in the exceptions per callable. For example, a function :code:`my_func()` calls two other functions, :code:`get_data()` and :code:`process_data()`, and in turn
	:code:`get_data()` calls another function, :code:`open_socket()`. In this scenario, the calls hierarchy is::

			my_func            <- depth = 0
			├get_data          <- depth = 1
			│└open_socket      <- depth = 2
			└process_data      <- depth = 1

	Setting :code:`depth=0` means that only exceptions raised by :code:`my_func()` are going to be included in the documentation; Setting :code:`depth=1` means that only exceptions raised by :code:`my_func()`, :code:`get_data()`
	and :code:`process_data()` are going to be included in the documentation; and finally setting :code:`depth=2` (in this case it has the same effects as :code:`depth=None`) means that only exceptions raised by :code:`my_func()`,
	:code:`get_data()`, :code:`process_data()` and :code:`open_socket()` are going to be included in the documentation.

	:rtype: non-negative integer
	:raises: RuntimeError (Argument \\`depth\\` is not valid)
	"""	#pylint: disable=W0105

	exclude = property(_get_exclude, _set_exclude, None, doc='Modules and callables to exclude')
	"""
	Gets or sets the default list of (potentially partial) module and callable names to exclude from exceptions per callable. For example, :code:`['putil.ex']` excludes all exceptions from modules :code:`putil.exh` and
	:code:`putil.exdoc` (it acts as :code:`r'putil.ex*'`).  In addition to these modules, :code:`['putil.ex', 'putil.eng.peng']` excludes exceptions from the function :code:`putil.eng.peng`.

	:rtype: list
	:raises: RuntimeError (Argument \\`exclude\\` is not valid)
	"""	#pylint: disable=W0105
