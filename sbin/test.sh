#!/bin/bash
# test.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "test.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  test.sh [-h] [-n num-cpus] [-c] [-d] [module-name] [test-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -c  Measure test coverage ([test-name] illegal)" >&2
	echo -e "  -d  Verify doctests ([module-name] and [test-name] illegal)" >&2
	echo -e "  -n  Number of CPUs to use (greater than 2)" >&2
	echo -e "" >&2
	echo -e "If no module name is given all package modules are processed." >&2
	echo -e "Coverage and doctest verification are mutually exclusive." >&2
}

# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "${source}" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "${source}" )" && pwd )"
	source="$(readlink "${source}")"
	[[ ${source} != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "${source}" )" && pwd )"
pkg_dir=$(dirname ${dir})
src_dir=${pkg_dir}/putil
cpwd=${PWD}

source ${pkg_dir}/sbin/functions.sh

# Read command line options
num_cpus=""
coverage=0
doctest=0
while getopts ":hcdn:" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		c)
			coverage=1
			;;
		d)
			doctest=1
			;;
		n)
			num_cpus=${OPTARG}
			;;
		\?)
			echo "test.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "${coverage}" == 1 ] && [ "${doctest}" == 1 ]; then
	echo "test.sh: coverage and doctests cannot be measured simultaneously"
	exit 1
fi
if [ "${doctest}" == 1 ] && [ "$#" -gt 0 ]; then
	echo "test.sh: too many command line arguments" >&2
	exit 1
fi
if [ "${coverage}" == 0 ] && [ "$#" -gt 2 ]; then
	echo "test.sh: too many command line arguments" >&2
	exit 1
fi
if [ "${coverage}" == 1 ] && [ "$#" -gt 1 ]; then
	echo "test.sh: too many command line arguments" >&2
	exit 1
fi


# Argument validation
module=""
if [ "$#" -gt 0 ]; then
	module=$1
	file=${pkg_dir}/tests/test_${module}.py
	if [ ! -f "${file}" ]; then
		echo "test.sh: test bench for module ${module} could not be found"
		exit 1
	fi
	module="test_${module}.py"
fi
koption=""
if [ "$#" == 2 ]; then
	koption="-k $2"
fi
noption=""
if [ "${num_cpus}" != "" ]; then
	num_cpus=$(echo "${num_cpus}" | grep "^[2-9][0-9]*$")
	if [ "${num_cpus}" == "" ]; then
		echo "test.sh: number of CPUs has to be an intenger greater than 1"
		exit 1
	fi
	if ! pip freeze | grep -q pytest-xdist; then
		echo 'test.sh: pytest-xdist needs to be installed to use multiple CPUS'
		exit 1
	fi
	noption="-n ${num_cpus}"
fi
poptions=""
if [ "${doctest}" == 1 ]; then
	print_banner "Doctests"
	poptions="--doctest-glob='*.rst' ${pkg_dir}/.tox/py27/lib/python2.7/site-packages/docs"
	tox -- ${noption} ${koption} ${poptions} ${module}
	ecode=$?
	if [ "${ecode}" == 0 ]; then
		poptions="--doctest-modules ${pkg_dir}/.tox/py27/lib/python2.7/site-packages/putil/"
		tox -- ${noption} ${koption} ${poptions} ${module}
	fi
elif [ "${coverage}" == 0 ]; then
	print_banner "Unit tests"
	poptions="-x -s -vv"
	tox -- ${noption} ${koption} ${poptions} ${module}
else
	print_banner "Coverage"
	rtype="term"
	if [ "${module}" != "" ]; then
		poptions="-x -s -vv --cov-config ${pkg_dir}/.coveragerc_tox --cov ${pkg_dir}/.tox/py27/lib/python2.7/site-packages/putil/ --cov-report html"
	else
		poptions="--cov-config ${pkg_dir}/.coveragerc_tox --cov ${pkg_dir}/.tox/py27/lib/python2.7/site-packages/putil/ --cov-report term"
	fi
	tox -- ${noption} ${koption} ${poptions} ${module}
fi
ecode=$?
cd ${cpwd}
if [ "${ecode}" != 0 ]; then
	exit 1
fi
