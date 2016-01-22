#!/usr/bin/env python
# rebase.py
# Copyright (c) 2013-2016 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,F0401,R0914,W0141


# Standard library imports
from __future__ import print_function
import argparse
import difflib
import os
import shutil
import stat
import sys
# Putil imports
import sbin.functions


###
# Functions
###
def diff(file1, file2):
    """ Diff two files """
    with open(file1, 'r') as fobj1:
        flines1 = [item.rstrip() for item in fobj1.readlines()]
    with open(file2, 'r') as fobj2:
        flines2 = [item.rstrip() for item in fobj2.readlines()]
    diff_list = list(
        difflib.unified_diff(flines1, flines2, fromfile=file1, tofile=file2)
    )
    return not bool(not diff_list)


def get_current_branch():
    """ Get git current branch """
    stdout = sbin.functions.shcmd(
        ['git', 'branch', '--list', '--no-color'],
        'Cannot get branch names'
    )
    branches = [
        item.strip() for item in stdout.split()
    ]
    for num, item in enumerate(branches):
        if item == '*':
            return branches[num+1]
    raise RuntimeError('Current Git branch could not be determined')


def rebase(pkg_dir, output_dir, obranch, rbranch):
    """ Rebase branch """
    stdout = sbin.functions.shcmd(
        ['git', 'rev-list', '--first-parent', '^'+obranch, rbranch],
        'Branches do not have common ancestor'
    )
    if get_current_branch() != rbranch:
        raise RuntimeError('Current branch is not branch to rebase')
    commits = [item.strip() for item in stdout.split()]
    files = []
    for commit in commits:
        stdout = sbin.functions.shcmd(
            [
                'git',
                'diff-tree',
                '--no-commit-id',
                '--name-only',
                '-r',
                commit
            ],
            'Cannot get commit files for {0}'.format(commit)
        )
        cfiles = [item.strip() for item in stdout.split()]
        files.extend(cfiles)
    files = sorted(list(set(files)))
    output_dir = os.path.abspath(output_dir)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    diff_script = ['#!/bin/bash\n']
    del_script = ['#!/bin/bash\n']
    for item in files:
        sfile = os.path.join(pkg_dir, item)
        dfile = os.path.join(output_dir, item)
        if not os.path.exists(sfile):
            del_script.append('rm -rf '+sfile+'\n')
        elif diff(sfile, dfile):
            ddir = os.path.dirname(dfile)
            if not os.path.exists(ddir):
                os.makedirs(ddir)
            shutil.copy(sfile, dfile)
            diff_script.append('meld '+sfile+' '+dfile+'\n')
    if len(del_script) > 1:
        sfile = os.path.join(output_dir, 'rmfiles.sh')
        with open(sfile, 'w') as fobj:
            fobj.writelines(del_script)
        cst = os.stat(sfile)
        os.chmod(sfile, cst.st_mode | stat.S_IXUSR)
    if len(diff_script) > 1:
        sfile = os.path.join(output_dir, 'diff.sh')
        with open(sfile, 'w') as fobj:
            fobj.writelines(diff_script)
        cst = os.stat(sfile)
        os.chmod(sfile, cst.st_mode | stat.S_IXUSR)


def valid_branch(branch):
    """ Argparse checker for branch name """
    branch = branch.strip()
    stdout = sbin.functions.shcmd(
        ['git', 'branch', '--list', '--no-color'],
        'Cannot verify branch'
    )
    branches = [
        item.strip() for item in stdout.split() if item.strip() != '*'
    ]
    branches.append('master')
    branches = list(set(branches))
    if branch not in branches:
        raise argparse.ArgumentTypeError(
            'Branch {0} does not exist'.format(branch)
        )
    return branch


if __name__ == "__main__":
    PKG_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PARSER = argparse.ArgumentParser(
        description='Rebase Git branch'
    )
    PARSER.add_argument(
        '-d', '--directory',
        help=(
            'directory where branch files are copied to '
            '(default ${{HOME}}/rebase)'
        ),
        nargs=1,
        default=[os.path.join(os.environ['HOME'], 'rebase')]
    )
    PARSER.add_argument(
        '-r', '--rebase_branch',
        help='branch to rebase',
        type=valid_branch,
        nargs=1,
    )
    PARSER.add_argument(
        '-o', '--origin_branch',
        help='origin branch',
        type=valid_branch,
        nargs=1,
    )
    ARGS = PARSER.parse_args()
    sys.exit(
        rebase(
            PKG_DIR,
            ARGS.directory[0],
            ARGS.origin_branch[0],
            ARGS.rebase_branch[0]
        )
    )
