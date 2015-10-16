#!/usr/bin/env python
# requirements_to_rst.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,R0912,R0914,R0915

import os


def proc_requirements(mobj):
    """ Get requirements in reStructuredText format """
    pkg_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    )
    deps = {
        'cogapp':{
            'name':'Cog',
            'py27':False,
            'optional':False,
            'url':''
        },
        'coverage':{
            'name':'Coverage',
            'py27':False,
            'optional':False,
            'url':'http://coverage.readthedocs.org/en/coverage-4.0a5'
        },
        'decorator':{
            'name':'Decorator',
            'py27':False,
            'optional':False,
            'url':'https://pythonhosted.org/decorator'
        },
        'funcsigs':{
            'name':'Funcsigs',
            'py27':True,
            'optional':False,
            'url':'https://pypi.python.org/pypi/funcsigs'
        },
        'matplotlib':{
            'name':'Matplotlib',
            'py27':False,
            'optional':False,
            'url':'http://matplotlib.org'
        },
        'mock':{
            'name':'Mock',
            'py27':True,
            'optional':False,
            'url':'http://www.voidspace.org.uk/python/mock'
        },
        'numpy':{
            'name':'Numpy',
            'py27':False,
            'optional':False,
            'url':'http://www.numpy.org'
        },
        'pillow':{
            'name':'Pillow',
            'py27':False,
            'optional':False,
            'url':'https://python-pillow.github.io'
        },
        'pycontracts':{
            'name':'PyContracts',
            'py27':False,
            'optional':False,
            'url':''
        },
        'pytest':{
            'name':'Py.test',
            'py27':False,
            'optional':False,
            'url':''
        },
        'pytest-cov':{
            'name':'Pytest-coverage',
            'py27':False,
            'optional':False,
            'url':'https://pypi.python.org/pypi/pytest-cov'
        },
        'pytest-xdist':{
            'name':'Pytest-xdist',
            'py27':False,
            'optional':True,
            'url':'https://pypi.python.org/pypi/pytest-xdist'
        },
        'scipy':{
            'name':'Scipy',
            'py27':False,
            'optional':False,
            'url':'http://www.scipy.org'
        },
        'six':{
            'name':'Six',
            'py27':False,
            'optional':False,
            'url':'https://pythonhosted.org/six'
        }
    }
    fname = os.path.join(pkg_dir, 'requirements.txt')
    with open(fname, 'r') as fobj:
        lines = sorted(
            [
                item.lower().strip() for item in fobj.readlines()
                if not item.startswith('#')
            ]
        )
    olines = ['']
    for line in lines:
        tokens = line.split('>=')
        oper = '>='
        if len(tokens) == 1:
            tokens = line.split('==')
            oper = '=='
        pkg_name = tokens[0]
        ver = tokens[1]
        url = (
            ' <{0}>'.format(deps[pkg_name]['url'])
            if deps[pkg_name]['url'] else
            ''
        )
        par = ''
        if deps[pkg_name]['py27'] or deps[pkg_name]['optional']:
            tmp = []
            tmp += ['optional'] if deps[pkg_name]['optional'] else []
            tmp += ['only for Python 2.7'] if deps[pkg_name]['py27'] else []
            par = ' ('+(', '.join(tmp))+')'
        olines.append(
            '    * `{name}{url}`_\n      {oper} {ver}{par}\n'.format(
                name=deps[pkg_name]['name'],
                url=url,
                oper=oper,
                ver=ver,
                par=par
            )
        )
    mobj.out('\n'.join(olines)+'\n')
