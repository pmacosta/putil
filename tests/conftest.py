# conftest.py
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

import os, pickle, pytest, __builtin__

import putil.exh


###
# Functions
###
def log(line, append=True):
	""" xdist debugging function """
	with open(os.path.join(os.environ['HOME'], 'xdist-debug.log'), 'a' if append else 'w') as fobj:
		fobj.write('{0}\n'.format(line))


def pytest_configure(config):
	""" Pytest configuration, both for the slave and master """
	if not hasattr(config, "slaveinput"):	# Master configuration
		pass


def pytest_configure_node(node):	#pylint: disable=W0613
	""" Per node configuration """
	if hasattr(__builtin__, '_EXDOC_EXCLUDE'):
		node.slaveinput['exclude'] = pickle.dumps(__builtin__._EXDOC_EXCLUDE)	#pylint: disable=E1101,W0212
	if hasattr(__builtin__, '_EXDOC_FULL_CNAME'):
		node.slaveinput['full_cname'] = pickle.dumps(__builtin__._EXDOC_FULL_CNAME)	#pylint: disable=E1101,W0212


def pytest_testnodedown(node, error):
	""" Integrate received exception handler form sub-process into main one """
	if error:
		raise RuntimeError('Slave node reported an error')
	if 'msg' in node.slaveoutput:
		obj = pickle.loads(node.slaveoutput['msg'])
		if not hasattr(__builtin__, '_EXH_LIST'):	#pylint: disable=E1101,W0212
			setattr(__builtin__, '_EXH_LIST', [obj])
		else:
			getattr(__builtin__, '_EXH_LIST').append(obj)	#pylint: disable=E1101,W0212


@pytest.fixture(autouse=True, scope="module")
def exhobj(request):
	"""
	Fixture to a) get the global exception handler in sub-process and b) send the exception handler after tests done
	This fixture runs in the slave session with NO connection to master except through slaveinput/slaveoutput
	"""
	xdist_run = hasattr(request.config, 'slaveinput')
	def fin():
		""" Tear down function """
		if hasattr(request.config, 'slaveoutput') and hasattr(request.module.__builtin__, '_EXH'):
			request.config.slaveoutput['msg'] = pickle.dumps(getattr(request.module.__builtin__, '_EXH'))
	request.addfinalizer(fin)
	if xdist_run: # sub-process
		if not hasattr(request.module, '__builtin__'):
			setattr(request.module, '__builtin__', __import__('__builtin__'))
		exclude = pickle.loads(request.config.slaveinput['exclude']) if 'exclude' in request.config.slaveinput else None
		full_cname = pickle.loads(request.config.slaveinput['full_cname']) if 'full_cname' in request.config.slaveinput else False
		setattr(request.module.__builtin__, '_EXH', putil.exh.ExHandle(full_cname=full_cname, exclude=exclude))
