# functions.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1111,R0904,W0201,W0621

import glob
import json
import os
import sys

if sys.hexversion < 0x03000000:
    from putil.compat2 import _unicode_to_ascii


###
# Global variables
###
SUPPORTED_VERS = ['2.6', '2.7', '3.3', '3.4', '3.5']


###
# Functions
###
def get_pkg_data_files(share_dir):
    """ Create data_files setup.py argument """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fdata = json_load(os.path.join('data', 'data_files.json'))
    rdict = {}
    # For each directory a single list with all the file names in that
    # directory has to be provided, otherwise if multiple entries with
    # lists are provided only the last list is installed
    rdict = dict([(fdir, []) for fdir in set([item['dir'] for item in fdata])])
    for fdict in fdata:
        rdict[fdict['dir']] = rdict[fdict['dir']]+(
            glob.glob(os.path.join(pkg_dir, fdict['dir'], fdict['file']))
        )
    return [
        (os.path.join(share_dir, fdir), rdict[fdir])
        for fdir in sorted(rdict.keys())
    ]


def gen_manifest(make_wheel=False):
    """ Generate MANIFEST.in file """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fdata = json_load(os.path.join('data', 'data_files.json'))
    ret = [
        '# MANIFEST.in',
        '# Copyright (c) 2013-2015 Pablo Acosta-Serafini',
        '# See LICENSE for details'
    ]
    if not make_wheel:
        for fdict in fdata:
            star = '*' in fdict['file']
            ret.append(
                '{rec}include{fdir}{pattern}'.format(
                    rec='recursive-' if star else '',
                    fdir=(
                        ' {fdir}{sep}'.format(
                            fdir=fdict['dir'],
                            sep='/' if fdict['dir'] and (not star) else ''
                        )
                        if fdict['dir'] else
                        ''
                    ),
                    pattern=(
                        '{sep}{fname}'.format(
                            sep=' ' if star or (not fdict['dir']) else '',
                            fname=fdict['file']
                        )
                    )
                )
            )
    with open(os.path.join(pkg_dir, 'MANIFEST.in'), 'w') as fobj:
        fobj.writelines('\n'.join(ret))


def json_load(fname):
    """ Load JSON file """
    pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_file = os.path.join(pkg_dir, fname)
    with open(conf_file, 'r') as fobj:
        fdata = json.load(fobj)
    if sys.hexversion < 0x03000000:
        fdata = _unicode_to_ascii(fdata)
    return fdata


def load_requirements(pkg_dir, pyver, cat='source'):
    """ Get package names from requirements files """
    pyver = pyver.replace('.', '')
    reqs_dir = os.path.join(pkg_dir, 'requirements')
    if cat.lower() == 'source':
        reqs_files = ['main_py{0}.pip'.format(pyver)]
    elif cat.lower() == 'testing':
        reqs_files = [
            'main_py{0}.pip'.format(pyver),
            'tests_py{0}.pip'.format(pyver),
            'docs.pip',
        ]
    else:
        raise RuntimeError('Unknown requirements category: {0}'.format(cat))
    ret = []
    for fname in [os.path.join(reqs_dir, item) for item in reqs_files]:
        with open(os.path.join(reqs_dir, fname), 'r') as fobj:
            lines = [
                item.strip()
                for item in fobj.readlines()
                if item.strip()
            ]
        ret.extend(lines)
    return ret


def python_version(hver):
    """ Return Python version """
    return '{major}.{minor}'.format(major=int(hver[:-2]), minor=int(hver[-2:]))
