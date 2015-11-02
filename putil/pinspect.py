# pinspect.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,E0611,F0401,R0912,W0212,W0631

from __future__ import print_function
import ast
import collections
import copy
import json
try:    # pragma: no cover
    from funcsigs import signature
except ImportError: # pragma: no cover
    from inspect import signature
import os
import re
import sys
import types

if sys.hexversion < 0x03000000: # pragma: no cover
    from putil.compat2 import _unicode_to_ascii, _readlines, _unicode_char
else:   # pragma: no cover
    from putil.compat3 import _readlines, _unicode_char


###
# Global constants
###
_PRIVATE_PROP_REGEXP = re.compile('_[^_]+')


###
# Functions
###
def _get_module_name_from_fname(fname):
    """ Get module name from module file name """
    iobj = [
        item
        for item in sys.modules.values()
        if item and hasattr(item, '__file__')
    ]
    fname = fname.replace('.pyc', '.py')
    for mobj in iobj:
        if mobj.__file__.replace('.pyc', '.py') == fname:
            module_name = mobj.__name__
            return module_name
    raise RuntimeError('Module could not be found')


def _is_parg(arg):
    """
    Returns True if arg argument is the name of a positional variable
    argument (i.e. *pargs)
    """
    return (len(arg) > 1) and (arg[0] == '*') and (arg[1] != '*')


def _is_kwarg(arg):
    """
    Returns True if arg argument is the name of a keyword variable argument
    (i.e. **kwargs)
    """
    return (len(arg) > 2) and (arg[:2] == '**')


def _validate_fname(fname):
    """ Validates that a string is a valid file name """
    msg = 'Argument `callables_fname` is not valid'
    if not isinstance(fname, str):
        raise RuntimeError(msg)
    try:
        if not os.path.exists(fname):
            os.access(fname, os.W_OK)
    except (TypeError, ValueError): # pragma: no cover
        raise RuntimeError(msg)


def get_function_args(func, no_self=False, no_varargs=False):
    """
    Returns a tuple of the function argument names in the order they are
    specified in the function signature

    :param func: Function
    :type  func: function object

    :param no_self: Flag that indicates whether the function argument *self*,
                    if present, is included in the output (False) or not (True)
    :type  no_self: boolean

    :param no_varargs: Flag that indicates whether keyword arguments are
                       included in the output (True) or not (False)
    :type  no_varargs: boolean

    :rtype: tuple

    For example:

        >>> import putil.pinspect
        >>> class MyClass(object):
        ...     def __init__(self, value, **kwargs):
        ...         pass
        ...
        >>> putil.pinspect.get_function_args(MyClass.__init__)
        ('self', 'value', '**kwargs')
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_self=True
        ... )
        ('value', '**kwargs')
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_self=True, no_varargs=True
        ... )
        ('value',)
        >>> putil.pinspect.get_function_args(
        ...     MyClass.__init__, no_varargs=True
        ... )
        ('self', 'value')
    """
    par_dict = signature(func).parameters
    # Mark positional and/or keyword arguments (if any)
    args = [
        '{prefix}{arg}'.format(
            prefix=(
                '*'
                if par_dict[par].kind == par_dict[par].VAR_POSITIONAL else
                (
                    '**'
                    if par_dict[par].kind == par_dict[par].VAR_KEYWORD else
                    ''
                )
            ),
            arg=par
        )
        for par in par_dict
    ]
    # Filter out 'self' from parameter list (optional)
    self_filtered_args = args if not args else (
        args[1 if (args[0] == 'self') and no_self else 0:]
    )
    # Filter out positional or keyword arguments (optional)
    varargs_filtered_args = tuple([
        arg
        for arg in self_filtered_args
        if ((not no_varargs) or
           (no_varargs and (not _is_parg(arg)) and (not _is_kwarg(arg))))
    ])
    return varargs_filtered_args


def get_module_name(module_obj):
    r"""
    Retrieves the module name from a module object

    :param module_obj: Module object
    :type  module_obj: object

    :rtype: string

    :raises:
     * RuntimeError (Argument \`module_obj\` is not valid)

     * RuntimeError (Module object \`*[module_name]*\` could not be found in
       loaded modules)

    For example:

        >>> import putil.pinspect
        >>> putil.pinspect.get_module_name(sys.modules['putil.pinspect'])
        'putil.pinspect'
    """
    if not is_object_module(module_obj):
        raise RuntimeError('Argument `module_obj` is not valid')
    name = module_obj.__name__
    if name not in sys.modules:
        raise RuntimeError(
            (
                'Module object `{name}` could not '
                'be found in loaded modules'.format(name=name)
            )
        )
    return name


def is_object_module(obj):
    """
    Tests if the argument is a module object

    :param obj: Object
    :type  obj: any

    :rtype: boolean
    """
    return isinstance(obj, types.ModuleType)


def is_special_method(name):
    """
    Tests if a callable name is a special Python method (has a :code:`'__'`
    prefix and suffix)

    :param name: Callable name
    :type  name: string

    :rtype: boolean
    """
    return name.startswith('__')


def private_props(obj):
    """
    Yields private properties of an object. A private property is
    defined as one that has a single underscore (:code:`_`) before its name

    :param obj: Object
    :type  obj: object

    :returns: iterator
    """
    # Get private properties but NOT magic methods
    iobj = [
        obj_name
        for obj_name in dir(obj)
        if _PRIVATE_PROP_REGEXP.match(obj_name) and
            (not callable(getattr(obj, obj_name)))
    ]
    for obj_name in iobj:
        yield obj_name


###
# Classes
###
class Callables(object):
    r"""
    Generates a list of module callables (functions, classes, methods and class
    properties) and gets their attributes (callable type, file name, lines
    span). Information from multiple modules can be stored in the callables
    database of the object by repeatedly calling
    :py:meth:`putil.pinspect.Callables.trace` with different module file names.
    A :py:class:`putil.pinspect.Callables` object retains knowledge of which
    modules have been traced so repeated calls to
    :py:meth:`putil.pinspect.Callables.trace` with the *same* module object
    will *not* result in module re-traces (and the consequent performance hit)

    :param fnames: File names of the modules to trace. If None no immediate
                   tracing is done
    :type  fnames: list of strings or None

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`fnames\` is not valid)
    """
    # pylint: disable=R0903
    def __init__(self, fnames=None):
        self._callables_db = {}
        self._reverse_callables_db = {}
        self._modules_dict = {}
        self._fnames = {}
        self._module_names = []
        self._class_names = []
        if fnames:
            self.trace(fnames)

    def __add__(self, other):
        """
        Merges two objects

        :raises: RuntimeError (Conflicting information between objects)

        For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
            >>> obj3 = putil.pinspect.Callables([
            ... sys.modules['putil.exh'].__file__,
            ... sys.modules['putil.eng'].__file__,
            ... ])
            >>> obj1 == obj3
            False
            >>> obj1 == obj2
            False
            >>> obj1+obj2 == obj3
            True
        """
        self._check_intersection(other)
        robj = Callables()
        robj._callables_db = copy.deepcopy(self._callables_db)
        robj._callables_db.update(copy.deepcopy(other._callables_db))
        robj._reverse_callables_db = copy.deepcopy(self._reverse_callables_db)
        robj._reverse_callables_db.update(
            copy.deepcopy(other._reverse_callables_db)
        )
        robj._modules_dict = copy.deepcopy(self._modules_dict)
        robj._modules_dict.update(copy.deepcopy(other._modules_dict))
        robj._module_names = list(
            set(self._module_names[:]+other._module_names[:])
        )
        robj._class_names = list(
            set(self._class_names[:]+other._class_names[:])
        )
        robj._fnames = copy.deepcopy(self._fnames)
        robj._fnames.update(copy.deepcopy(other._fnames))
        return robj

    def __bool__(self): # pragma: no cover
        """
        Returns :code:`False` if no modules have been traced, :code:`True`
        otherwise. For example:

            >>> from __future__ import print_function
            >>> import putil.eng, putil.pinspect, sys
            >>> obj = putil.pinspect.Callables()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> obj.trace([sys.modules['putil.eng'].__file__])
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._module_names)

    def __copy__(self):
        """
        Copies object. For example:

            >>> import copy, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = copy.copy(obj1)
            >>> obj1 == obj2
            True
        """
        cobj = Callables()
        for prop_name in private_props(self):
            setattr(cobj, prop_name, copy.deepcopy(getattr(self, prop_name)))
        return cobj

    def __eq__(self, other):
        """
        Tests object equality. For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj3 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
            >>> obj1 == obj2
            True
            >>> obj1 == obj3
            False
            >>> 5 == obj3
            False
        """
        return isinstance(other, Callables) and all([
            sorted(getattr(self, attr)) == sorted(getattr(other, attr))
            for attr in private_props(self)]
        )

    def __iadd__(self, other):
        """
        Merges an object into an existing object

        :raises: RuntimeError (Conflicting information between objects)

        For example:

            >>> import putil.eng, putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> obj2 = putil.pinspect.Callables(
            ...     [sys.modules['putil.eng'].__file__]
            ... )
            >>> obj3 = putil.pinspect.Callables([
            ...     sys.modules['putil.exh'].__file__,
            ...     sys.modules['putil.eng'].__file__,
            ... ])
            >>> obj1 == obj3
            False
            >>> obj1 == obj2
            False
            >>> obj1 += obj2
            >>> obj1 == obj3
            True
        """

        self._check_intersection(other)
        self._callables_db.update(copy.deepcopy(other._callables_db))
        self._reverse_callables_db.update(
            copy.deepcopy(other._reverse_callables_db)
        )
        self._modules_dict.update(copy.deepcopy(other._modules_dict))
        self._module_names = list(
            set(self._module_names+other._module_names[:])
        )
        self._class_names = list(set(self._class_names+other._class_names[:]))
        self._fnames.update(copy.deepcopy(other._fnames))
        return self

    def __nonzero__(self):  # pragma: no cover
        """
        Returns :code:`False` if no modules have been traced, :code:`True`
        otherwise. For example:

            >>> from __future__ import print_function
            >>> import putil.eng, putil.pinspect, sys
            >>> obj = putil.pinspect.Callables()
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
            >>> obj.trace([sys.modules['putil.eng'].__file__])
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
        """
        return bool(self._module_names)

    def __repr__(self):
        """
        Returns a string with the expression needed to re-create the object.
        For example:

            >>> import putil.exh, putil.pinspect, sys
            >>> obj1 = putil.pinspect.Callables(
            ...     [sys.modules['putil.exh'].__file__]
            ... )
            >>> repr(obj1)  #doctest: +ELLIPSIS
            "putil.pinspect.Callables(['...exh.py'])"
            >>> exec("obj2="+repr(obj1))
            >>> obj1 == obj2
            True

        """
        return 'putil.pinspect.Callables({0})'.format(
            sorted(self._fnames.keys())
        )

    def __str__(self):
        """
        Returns a string with a detailed description of the object's contents.
        For example:

            >>> from __future__ import print_function
            >>> import putil.pinspect, os, sys
            >>> import docs.support.pinspect_example_1
            >>> cobj = putil.pinspect.Callables([
            ...     sys.modules['docs.support.pinspect_example_1'].__file__
            ... ])
            >>> print(cobj) #doctest: +ELLIPSIS
            Modules:
               ...pinspect_example_1
            Classes:
               ...pinspect_example_1.my_func.MyClass
            ...pinspect_example_1.my_func: func (9-25)
            ...pinspect_example_1.my_func.MyClass: class (11-25)
            ...pinspect_example_1.my_func.MyClass.__init__: meth (18-20)
            ...pinspect_example_1.my_func.MyClass._get_value: meth (21-23)
            ...pinspect_example_1.my_func.MyClass.value: prop (24-25)
            ...pinspect_example_1.print_name: func (26-27)

        The numbers in parenthesis indicate the line number in which the
        callable starts and ends within the file it is defined in
        """
        ret = list()
        if self._module_names:
            # List traced modules
            ret.append('Modules:')
            for module_name in sorted(self._module_names):
                ret.append(
                    '   {module_name}'.format(module_name=module_name)
                )
            # List traced classes
            if self._class_names:
                ret.append('Classes:')
                for class_name in sorted(self._class_names):
                    ret.append(
                        '   {class_name}'.format(class_name=class_name)
                    )
            # List traced callables (methods, functions, properties)
            for entry in sorted(self._modules_dict):
                dict_value = self._modules_dict[entry]
                for value in sorted(dict_value, key=lambda x: x['code_id'][1]):
                    start_line = value['code_id'][1]
                    stop_line = value['last_lineno']
                    line_text = (
                        (
                            ' ({start_line}-{stop_line})'.format(
                                start_line=start_line,
                                stop_line=stop_line
                            )
                        )
                        if start_line != stop_line else
                        ' ({line_number})'.format(line_number=start_line)
                    )
                    ret.append(
                        '{callable_name}: {callable_type}{line_range}'.format(
                            callable_name=value['name'],
                            callable_type=value['type'],
                            line_range=line_text
                        )
                    )
            return '\n'.join(ret)
        else:
            return ''

    def _check_intersection(self, other):
        """
        Check that intersection of two objects is congruent, i.e. that they
        have identical information in the intersection
        """
        # pylint: disable=W1504
        props = ['_callables_db', '_reverse_callables_db', '_modules_dict']
        for prop in props:
            self_dict = getattr(self, prop)
            other_dict = getattr(other, prop)
            keys_self = set(self_dict.keys())
            keys_other = set(other_dict.keys())
            intersection = keys_self & keys_other
            for key in intersection:
                if ((type(self_dict[key]) != type(other_dict[key])) or
                   ((type(self_dict[key]) == type(other_dict[key])) and
                   ((isinstance(self_dict[key], list) and
                   (not all(
                       [
                           item in self_dict[key] for item in other_dict[key]
                       ]
                   ))) or
                   (
                       isinstance(self_dict[key], dict) and
                       (self_dict[key] != other_dict[key])
                   ) or
                   (isinstance(self_dict[key], str) and
                   (self_dict[key] != other_dict[key]))))):
                    raise RuntimeError(
                        'Conflicting information between objects'
                    )

    def _get_callables_db(self):
        """ Getter for callables_db property """
        return self._callables_db

    def get_callable_from_line(self, module_file, lineno):
        """ Get the callable that the line number belongs to """
        module_name = _get_module_name_from_fname(module_file)
        if module_name not in self._modules_dict:
            self.trace([module_file])
        ret = None
        # Sort callables by starting line number
        iobj = sorted(
            self._modules_dict[module_name],
            key=lambda x: x['code_id'][1]
        )
        for value in iobj:
            if value['code_id'][1] <= lineno <= value['last_lineno']:
                ret = value['name']
            elif value['code_id'][1] > lineno:
                break
        return ret if ret else module_name

    def _get_reverse_callables_db(self):
        """ Getter for reverse_callables_db property """
        return self._reverse_callables_db

    def load(self, callables_fname):
        """
        Loads traced modules information from a `JSON
        <http://www.json.org/>`_ file. The loaded module information is merged
        with any existing module information

        :param callables_fname: File name
        :type  callables_fname: :ref:`FileNameExists`

        :raises:
         * OSError (File *[fname]* could not be found)

         * RuntimeError (Argument \\`callables_fname\\` is not valid)
        """
        # Validate file name
        _validate_fname(callables_fname)
        if not os.path.exists(callables_fname):
            raise OSError(
                'File {0} could not be found'.format(callables_fname)
            )
        with open(callables_fname, 'r') as fobj:
            fdict = json.load(fobj)
        if sys.hexversion < 0x03000000: # pragma: no cover
            fdict = _unicode_to_ascii(fdict)
        self._callables_db.update(fdict['_callables_db'])
        # Reverse the tuple-to-string conversion that the save method
        # does due to the fact that JSON keys need to be strings and the
        # keys of the reverse callable dictionary are tuples where the first
        # item is a file name and the second item is the starting line of the
        # callable within that file (dictionary value)
        rdict = {}
        for key, value in fdict['_reverse_callables_db'].items():
            tokens = key[1:-1].split(',')
            rdict[(tokens[0].strip()[1:-1], int(tokens[1]))] = value
        self._reverse_callables_db.update(rdict)
        self._modules_dict.update(fdict['_modules_dict'])
        self._fnames.update(fdict['_fnames'])
        self._module_names.extend(fdict['_module_names'])
        self._class_names.extend(fdict['_class_names'])
        self._module_names = sorted(list(set(self._module_names)))
        self._class_names = sorted(list(set(self._class_names)))

    def refresh(self):
        """
        Re-traces modules which have been modified since the time they were
        traced
        """
        self.trace(list(self._fnames.keys()), _refresh=True)

    def save(self, callables_fname):
        """
        Saves traced modules information to a `JSON`_ file. If
        the file exists it is overwritten

        :param callables_fname: File name
        :type  callables_fname: :ref:`FileName`

        :raises: RuntimeError (Argument \\`fname\\` is not valid)
        """
        # Validate file name
        _validate_fname(callables_fname)
        # JSON keys have to be strings but the reverse callables dictionary
        # keys are tuples, where the first item is a file name and the
        # second item is the starting line of the callable within that file
        # (dictionary value), thus need to convert the key to a string
        fdict = {
            '_callables_db': self._callables_db,
            '_reverse_callables_db':dict(
                [
                    (str(key), value)
                    for key, value in self._reverse_callables_db.items()
                ]
            ),
            '_modules_dict':self._modules_dict,
            '_fnames':self._fnames,
            '_module_names':self._module_names,
            '_class_names':self._class_names
        }
        with open(callables_fname, 'w') as fobj:
            json.dump(fdict, fobj)

    def trace(self, fnames, _refresh=False):
        r"""
        Generates a list of module callables (functions, classes, methods and
        class properties) and gets their attributes (callable type, file name,
        lines span)

        :param fnames: File names of the modules to trace
        :type  fnames: list

        :raises:
         * OSError (File *[fname]* could not be found)

         * RuntimeError (Argument \`fnames\` is not valid)
        """
        # pylint: disable=R0914
        if fnames and (not isinstance(fnames, list)):
            raise RuntimeError('Argument `fnames` is not valid')
        if fnames and any([not isinstance(item, str) for item in fnames]):
            raise RuntimeError('Argument `fnames` is not valid')
        for fname in fnames:
            if not os.path.exists(fname):
                raise OSError('File {0} could not be found'.format(fname))
        fnames = [item.replace('.pyc', '.py') for item in fnames]
        bobj = collections.namedtuple('Bundle', ['lineno', 'col_offset'])
        for fname in fnames:
            if ((fname not in self._fnames) or (_refresh and
                (fname in self._fnames)
                and (self._fnames[fname]['date'] < os.path.getmtime(fname)))):
                module_name = (
                    _get_module_name_from_fname(fname)
                    if not _refresh else
                    self._fnames[fname]['name']
                )
                # Remove old module information if it is going to be refreshed
                if _refresh:
                    self._module_names.pop(
                        self._module_names.index(module_name)
                    )
                    for cls in self._fnames[fname]['classes']:
                        self._class_names.pop(self._class_names.index(cls))
                    dlist = []
                    for key, value in self._reverse_callables_db.items():
                        if key[0] == fname:
                            dlist.append(key)
                            del self._callables_db[value]
                    for item in dlist:
                        del self._reverse_callables_db[item]
                lines = _readlines(fname)
                # Eliminate all Unicode characters till the first ASCII
                # character is found in first line of file, to deal with
                # Unicode-encoded source files
                for num, char in enumerate(lines[0]):   # pragma: no cover
                    if not _unicode_char(char):
                        break
                lines[0] = lines[0][num:]
                tree = ast.parse(''.join(lines))
                aobj = _AstTreeScanner(module_name, fname, lines)
                aobj.visit(tree)
                # Create a fake callable at the end of the file to properly
                # 'close', i.e. assign a last line number to the last
                # callable in file
                fake_node = bobj(len(lines)+1, -1)
                aobj._close_callable(fake_node, force=True)
                self._class_names += aobj._class_names[:]
                self._module_names.append(module_name)
                self._callables_db.update(aobj._callables_db)
                self._reverse_callables_db.update(aobj._reverse_callables_db)
                # Split into modules
                self._modules_dict[module_name] = []
                iobj = [
                    item
                    for item in self._callables_db.values()
                    if item['name'].startswith(module_name+'.')
                ]
                for entry in iobj:
                    self._modules_dict[module_name].append(entry)
                self._fnames[fname] = {
                    'name': module_name,
                    'date': os.path.getmtime(fname),
                    'classes':aobj._class_names[:]
                }

    # Managed attributes
    callables_db = property(
        _get_callables_db, doc='Module(s) callables database'
    )
    """
    Returns the callables database

    :rtype: dictionary

    The callable database is a dictionary that has the following structure:

    * **full callable name** *(string)* -- Dictionary key. Elements in the
      callable path are separated by periods (:code:`'.'`). For example, method
      :code:`my_method()` from class
      :code:`MyClass` from module :code:`my_module` appears as
      :code:`'my_module.MyClass.my_method'`

     * **callable properties** *(dictionary)* -- Dictionary value. The elements
       of this dictionary are:

      * **type** *(string)* -- :code:`'class'` for classes, :code:`'meth'` for
        methods, :code:`'func'` for functions or :code:`'prop'` for properties
        or class attributes

      * **code_id** *(tuple or None)* -- A tuple with the following items:

        * **file name** *(string)* -- the first item contains the file name
          where the callable can be found

        * **line number** *(integer)* -- the second item contains the line
          number in which the callable code starts (including decorators)

      * **last_lineno** *(integer)* -- line number in which the callable code
        ends (including blank lines and comments regardless of their
        indentation level)
    """
    reverse_callables_db = property(
        _get_reverse_callables_db, doc='Reverse module(s) callables database'
    )
    """
    Returns the reverse callables database

    :rtype: dictionary

    The reverse callable database is a dictionary that has the following
    structure:

     * **callable id** *(tuple)* -- Dictionary key. Two-element tuple in which
       the first tuple item is the file name where the callable is defined
       and the second tuple item is the line number where the callable
       definition starts

     * **full callable name** *(string)* -- Dictionary value. Elements in the
       callable path are separated by periods (:code:`'.'`). For example,
       method :code:`my_method()` from class :code:`MyClass` from module
       :code:`my_module` appears as :code:`'my_module.MyClass.my_method'`
    """


class _AstTreeScanner(ast.NodeVisitor):
    """
    Get all callables from a given module by traversing abstract syntax tree
    """
    # pylint: disable=R0902,W0702
    def __init__(self, mname, fname, lines):
        super(_AstTreeScanner, self).__init__()
        self._lines = lines
        self._wsregexp = re.compile(r'^(\s*).+')
        self._fname = fname.replace('.pyc', '.py')
        self._module = mname
        self._indent_stack = [{
            'level':0,
            'type':'module',
            'prefix':'',
            'full_name':None,
            'lineno':0
        }]
        self._callables_db = {}
        self._reverse_callables_db = {}
        self._class_names = []
        self._processed_line = 0
        ###
        # self._debug = True
        ###

    def _close_callable(self, node, force=False):
        """ Record last line number of callable """
        # Only nodes that have a line number can be considered for closing
        # callables. Similarly, only nodes with lines greater than the one
        # already processed can be considered for closing callables
        try:
            lineno = node.lineno
        except AttributeError:
            return
        if lineno <= self._processed_line:
            return
        # ### Print statements for debug
        # if self._debug:
        #     print(
        #         pcolor('Close callable @ line = {0}'.format(lineno), 'green')
        #     )
        # ###
        # Extract node name for property closing. Once a property is found,
        # it can only be closed out by a node type that has a name
        name = ''
        try:
            name = (
                node.name
                if hasattr(node, 'name') else (
                    node.targets[0].id
                    if hasattr(node.targets[0], 'id') else
                    node.targets[0].value.id
                )
            )
        except AttributeError:
            pass
        # Traverse backwards through call stack and close callables as needed
        indent = self._get_indent(node)
        count = -1
        # ### Print statements for debug
        # if self._debug:
        #     print(
        #         pcolor(
        #             '    Name {0} @ {1}, indent = {2}'.format(
        #                 name if name else 'None', lineno, indent
        #             ),
        #             'yellow'
        #         )
        #     )
        #     try:
        #         print(pprint_ast_node(node))
        #     except:
        #         pass
        # ###
        while count >= -len(self._indent_stack):
            element_full_name = self._indent_stack[count]['full_name']
            edict = self._callables_db.get(element_full_name, None)
            stack_indent = self._indent_stack[count]['level']
            open_callable = element_full_name and (not edict['last_lineno'])
            # ### Print statements for debug
            # if self._debug:
            #     print(
            #         pcolor(
            #             '    Name {0}, indent, {1}, stack_indent {2}'.format(
            #                 element_full_name, indent, stack_indent
            #             ),
            #             'yellow'
            #         )
            #     )
            # ###
            if (open_callable and (force or (indent < stack_indent) or
               ((indent == stack_indent) and
               ((edict['type'] != 'prop') or ((edict['type'] == 'prop') and
               (name and (name != element_full_name))))))):
                # ### Print statements for debug
                # if self._debug:
                #     print(
                #         pcolor(
                #             '    Closing {0} @ {1}'.format(
                #                 element_full_name, lineno-1
                #             ),
                #             'yellow'
                #         )
                #     )
                # ###
                edict['last_lineno'] = lineno-1
            if indent > stack_indent:
                break
            count -= 1

    def _get_indent(self, node):
        """ Get node indentation level """
        lineno = node.lineno
        if lineno > len(self._lines):
            return -1
        wsindent = self._wsregexp.match(self._lines[lineno-1])
        return len(wsindent.group(1))

    def _in_class(self, node):
        """ Find if callable is function or method """
        # Move left one indentation level and check if that callable is a class
        indent = self._get_indent(node)
        for indent_dict in reversed(self._indent_stack):    # pragma: no branch
            if ((indent_dict['level'] < indent) or
               (indent_dict['type'] == 'module')):
                return indent_dict['type'] == 'class'

    def _pop_indent_stack(self, node, node_type=None, action=None):
        """ Get callable full name """
        indent = self._get_indent(node)
        indent_stack = copy.deepcopy(self._indent_stack)
        # Find enclosing scope
        while (((indent <= indent_stack[-1]['level']) and
              (indent_stack[-1]['type'] != 'module')) or
              (indent_stack[-1]['type'] == 'prop')):
            self._close_callable(node)
            indent_stack.pop()
        # Construct new callable name
        name = (
            node.targets[0].id
            if hasattr(node.targets[0], 'id') else
            node.targets[0].value.id
        ) if node_type == 'prop' else node.name
        element_full_name = '.'.join([self._module]+[
            indent_dict['prefix']
            for indent_dict in indent_stack
            if indent_dict['type'] != 'module'
        ]+[name])+('({0})'.format(action) if action else '')
        # Add new callable entry to indentation stack
        self._indent_stack = indent_stack
        self._indent_stack.append({
            'level':indent,
            'prefix':name,
            'type':node_type,
            'full_name':element_full_name,
            'lineno':node.lineno
        })
        return element_full_name

    def generic_visit(self, node):
        """ Generic node """
        # ### Print statements for debug
        # if self._debug:
        #     print(pcolor('Enter generic visitor', 'magenta'))
        # ###
        # A generic visitor that potentially closes callables is needed to
        # close enclosed callables that are not at the end of the enclosing
        # callable, otherwise the ending line of the enclosed callable would
        # be the ending line of the enclosing callable, which would be
        # incorrect
        self._close_callable(node)
        super(_AstTreeScanner, self).generic_visit(node)

    def visit_arguments(self, node):
        # Decorated callables go to visit_FunctionDef in the first line of the
        # decorator, but the actual function definition would go the generic
        # visitor if it is not caught when processing the function arguments.
        # This would close the callable prematurely, so the argument walk needs
        # to be intercepted and suppressed
        pass

    def visit_Assign(self, node):
        """
        Assignment walker (to parse class properties defined via the
        property() function)
        """
        # ### Print statements for debug
        # if self._debug:
        #     print(pcolor('Enter assign visitor', 'magenta'))
        # ###
        # Class-level assignment may also be a class attribute that is not
        # a managed attribute, record it anyway, no harm in doing so as it
        # is not attached to a callable
        if self._in_class(node):
            element_full_name = self._pop_indent_stack(node, 'prop')
            code_id = (self._fname, node.lineno)
            self._processed_line = node.lineno
            self._callables_db[element_full_name] = {
                'name':element_full_name,
                'type':'prop',
                'code_id':code_id,
                'last_lineno':None
            }
            self._reverse_callables_db[code_id] = element_full_name
            # ### Print statements for debug
            # if self._debug:
            #     print(
            #         pcolor(
            #             'Visiting property {0} @ {1}'.format(
            #                 element_full_name, code_id[1]
            #             ),
            #             'green'
            #         )
            #     )
            ###
            # Get property actions
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """ Class walker """
        # ### Print statements for debug
        # if self._debug:
        #     print(pcolor('Enter class visitor', 'magenta'))
        # ###
        # Get class information (name, line number, etc.)
        element_full_name = self._pop_indent_stack(node, 'class')
        code_id = (self._fname, node.lineno)
        self._processed_line = node.lineno
        # Add class entry to dictionaries
        self._class_names.append(element_full_name)
        self._callables_db[element_full_name] = {
            'name':element_full_name,
            'type':'class',
            'code_id':code_id,
            'last_lineno':None
        }
        self._reverse_callables_db[code_id] = element_full_name
        # ### Print statements for debug
        # if self._debug:
        #     print(
        #         pcolor(
        #             'Visiting class {0} @ {1}, indent = {2}'.format(
        #                 element_full_name, code_id[1], self._get_indent(node)
        #             ),
        #             'green'
        #         )
        #     )
        # ###
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """ Function/method walker """
        # ### Print statements for debug
        # if self._debug:
        #     print(pcolor('Enter function visitor', 'magenta'))
        #     print(pprint_ast_node(node))
        # ###
        in_class = self._in_class(node)
        decorator_list = [
            dobj.id if hasattr(dobj, 'id') else dobj.attr
            for dobj in node.decorator_list
            if hasattr(dobj, 'id') or hasattr(dobj, 'attr')
        ]
        node.decorator_list = []
        # Callable can be:
        # a) A class property defined via decorated methods
        # b) A class method
        # c) A function
        # Get callable information (name, line number, etc.)
        action = ('getter' if 'property' in decorator_list else
                 ('setter' if 'setter' in decorator_list else
                 ('deleter' if 'deleter' in decorator_list else None)))
        element_type = 'meth' if in_class else 'func'
        element_full_name = self._pop_indent_stack(
            node, element_type, action=action
        )
        code_id = (self._fname, node.lineno)
        self._processed_line = node.lineno
        self._callables_db[element_full_name] = {
            'name':element_full_name,
            'type':element_type,
            'code_id':code_id,
            'last_lineno':None
        }
        self._reverse_callables_db[code_id] = element_full_name
        # ### Print statements for debug
        # if self._debug:
        #     print(
        #         pcolor(
        #             'Visiting callable {0}  @ {1}'.format(
        #                 element_full_name, code_id[1]
        #             ),
        #             'green'
        #         )
        #     )
        #     print(pcolor('    in_class = {}'.format(in_class), 'yellow'))
        # ###
        self.generic_visit(node)
