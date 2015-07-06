#!/usr/bin/env python
# coveragerc-manager.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0103

from __future__ import print_function
import os
import sys


###
# Global variables
###
SUBMODULES_LIST = ['plot']


###
# Functions
###
def _write(fobj, data):
    """ Simple file write """
    fobj.write(data)


def get_source_files(sdir):
    """
    Get Python source files that are not __init__.py and
    interpreter-specific
    """
    ver = 3 if sys.version_info.major == 2 else 2
    isf = []
    isf.append('conftest.py')
    isf.append('compat{0}.py'.format(ver))
    isf.append('datasource{0}.py'.format(ver))
    return [
        file_name
        for file_name in os.listdir(sdir)
        if file_name.endswith('.py') and (file_name != '__init__.py') and
        (not any([file_name.endswith(item) for item in isf]))
    ]


def main(argv): # pylint: disable=R0912,R0914,R0915
    """ Processing """
    debug = True
    env = argv[0]
    # Unpack command line arguments
    if env == 'tox':
        if len(argv[1:]) == 4:
            mode_flag, interp, pkg_dir, site_pkg_dir, submodules, module = (
                argv[1:]+[SUBMODULES_LIST, '']
            )
        else:
            mode_flag, interp, pkg_dir, module = argv[1:]+['']
    elif env == 'shippable':
        mode_flag, interp, pkg_dir, site_pkg_dir, submodules, module = (
            argv[1],
            argv[2],
            os.environ['SHIPPABLE_REPO_DIR'],
            argv[3],
            SUBMODULES_LIST,
            ''
        )
    elif env == 'local':
        if len(argv[1:]) == 4:
            mode_flag, interp, pkg_dir, site_pkg_dir, submodules, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                [argv[4]],
                argv[4]
            )
        else:
            mode_flag, interp, pkg_dir, site_pkg_dir, submodules, module = (
                argv[1],
                argv[2],
                argv[3],
                argv[3],
                [''],
                ''
            )
    # Generate .coveragerc file
    is_submodule = module in SUBMODULES_LIST
    source_dir = os.path.join(site_pkg_dir, 'putil')
    output_file_name = os.path.join(
        site_pkg_dir,
        'putil',
        '.coveragerc_{0}_{1}'.format(env, interp)
    )
    coverage_file_name = os.path.join(
        site_pkg_dir, 'putil', '.coverage_{}'.format(interp)
    )
    conf_file = []
    conf_file.append(os.path.join(source_dir, 'conftest.py'))
    conf_file.append(os.path.join(source_dir, 'plot', 'conftest.py'))
    if mode_flag == '1':
        lines = []
        lines.append(
            '# .coveragerc_{0} to control coverage.py during {1} runs'.format(
                env,
                env.capitalize()
            )
        )
        lines.append('[run]')
        lines.append('branch = True')
        lines.append('show_missing = True')
        lines.append('data_file = {}'.format(coverage_file_name))
        start_flag = True
        # Include modules
        source_files = get_source_files(os.path.join(site_pkg_dir, 'putil'))
        for file_name in [
                item
                for item in source_files
                if (env != 'local') or ((env == 'local') and
                   (not is_submodule) and (item == '{0}.py'.format(module)))]:
            start_flag, prefix = (
                (False, 'include = ')
                if start_flag else
                (False, 10*' ')
            )
            lines.append(
                '{0}{1}'.format(prefix, os.path.join(
                    site_pkg_dir,
                    'putil',
                    file_name
            )))
        # Include sub-modules
        if (env != 'local') or ((env == 'local') and is_submodule):
            for submodule in submodules:
                for file_name in [
                        item
                        for item in get_source_files(os.path.join(
                                site_pkg_dir,
                                'putil',
                                submodule))]:
                    start_flag, prefix = (
                        (False, 'include = ')
                        if start_flag else
                        (False, 10*' ')
                    )
                    lines.append('{0}{1}'.format(prefix, os.path.join(
                        site_pkg_dir,
                        'putil',
                        submodule,
                        file_name
                    )))
        # Generate XML reports for continuous integration
        if env == 'shippable':
            lines.append('[xml]')
            lines.append('output = {0}'.format(os.path.join(
                os.environ['SHIPPABLE_REPO_DIR'],
                'shippable',
                'codecoverage',
                'coverage.xml'
            )))
        # Write file
        with open(output_file_name, 'w') as fobj:
            _write(fobj, '\n'.join(lines))
        # Echo file
        if debug:
            print('File: {0}'.format(output_file_name))
            with open(output_file_name, 'r') as fobj:
                print(''.join(fobj.readlines()))
        # Generate conftest.py files to selectively
        # skip Python 2 or Python 3 files
        skip_file = (
            "import sys\n"
            "collect_ignore = []\n"
            "if sys.version_info.major == 2:\n"
            "   collect_ignore.append('compat3.py')\n"
            "else:\n"
            "   collect_ignore.append('compat2.py')\n"
        )
        with open(conf_file[0], 'w') as fobj:
            _write(fobj, skip_file)
        skip_file = (
            "import sys\n"
            "collect_ignore = []\n"
            "if sys.version_info.major == 2:\n"
            "   collect_ignore.append('datasource3.py')\n"
            "else:\n"
            "   collect_ignore.append('datasource2.py')\n"
        )
        with open(conf_file[1], 'w') as fobj:
            _write(fobj, skip_file)
    else:
        del_files = conf_file
        del_files.append(output_file_name)
        del_files.append(coverage_file_name)
        try:
            for fname in del_files:
                print('Deleting file {0}'.format(fname))
                os.remove(fname)
        except: #pylint: disable=W0702
            pass


if __name__ == '__main__':
    main(sys.argv[1:])
