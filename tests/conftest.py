# conftest.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,E1101,E1103,F0401,W0212

import os
import pickle
import pytest
import sys
if sys.version_info.major == 2:
    import __builtin__
else:
    import builtins as __builtin__

import putil.exh


###
# Functions
###
def log(line, append=True):
    """ xdist debugging function """
    with open(
            os.path.join(os.environ['HOME'], 'xdist-debug.log'),
            'a' if append else 'w'
    ) as fobj:
        fobj.write('{0}\n'.format(line))


def pytest_configure(config):
    """ Pytest configuration, both for the slave and master """
    if not hasattr(config, "slaveinput"):   # Master configuration
        pass


def pytest_configure_node(node):
    """ Per node configuration """
    # pylint: disable=W0613
    if hasattr(__builtin__, '_EXDOC_EXCLUDE'):
        node.slaveinput['exclude'] = pickle.dumps(__builtin__._EXDOC_EXCLUDE)
    if hasattr(__builtin__, '_EXDOC_FULL_CNAME'):
        node.slaveinput['full_cname'] = pickle.dumps(__builtin__._EXDOC_FULL_CNAME)


def pytest_testnodedown(node, error):
    """ Integrate received exception handler form sub-process into main one """
    if error:
        raise RuntimeError('Slave node reported an error')
    if 'msg' in node.slaveoutput:
        obj = pickle.loads(node.slaveoutput['msg'])
        if not hasattr(__builtin__, '_EXH_LIST'):
            setattr(__builtin__, '_EXH_LIST', [obj])
        else:
            getattr(__builtin__, '_EXH_LIST').append(obj)


@pytest.fixture(autouse=True, scope="module")
def exhobj(request):
    """
    Fixture to a) get the global exception handler in sub-process and b) send
    the exception handler after tests done
    This fixture runs in the slave session with NO connection to master except
    through slaveinput/slaveoutput
    """
    xdist_run = hasattr(request.config, 'slaveinput')
    def fin():
        """ Tear down function """
        if (hasattr(request.config, 'slaveoutput') and
           hasattr(request.module.__builtin__, '_EXH')):
            request.config.slaveoutput['msg'] = pickle.dumps(
                getattr(request.module.__builtin__, '_EXH')
            )
    request.addfinalizer(fin)
    if xdist_run: # sub-process
        modname = '__builtin__' if sys.version_info.major == 2 else 'builtins'
        if not hasattr(request.module, '__builtin__'):
            setattr(request.module, '__builtin__', __import__(modname))
        exclude = (pickle.loads(request.config.slaveinput['exclude'])
                  if 'exclude' in request.config.slaveinput else
                  None)
        full_cname = (pickle.loads(request.config.slaveinput['full_cname'])
                     if 'full_cname' in request.config.slaveinput else
                     False)
        setattr(
            request.module.__builtin__,
            '_EXH',
            putil.exh.ExHandle(full_cname=full_cname, exclude=exclude)
        )
