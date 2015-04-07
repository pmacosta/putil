#!/bin/bash
# coverage.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "coverage.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  coverage.sh [-h] [-n num-cpus] [module-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
	echo -e "  -n  Number of CPUs to use (greater than 2)" >&2
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

# Read command line options
num_cpus=""
while getopts ":hn:" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		n)
			num_cpus=${OPTARG}
			;;
		\?)
			echo "coverage.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" == 0 ]; then
	echo "coverage.sh: no module to measure test coverage" >&2
	exit 1
fi
if [ "$#" -gt 1 ]; then
	echo "coverage.sh: too many command line arguments" >&2
	exit 1
fi

# Argument validation
module=$1
file=${pkg_dir}/tests/test_${module}.py
if [ ! -f "${file}" ]; then
	echo "coverage.sh: test bench for module ${module} could not be found"
	exit 1
fi
noption=""
if [ "${num_cpus}" != "" ]; then
	num_cpus=$(echo "${num_cpus}" | grep "^[2-9][0-9]*$")
	if [ "${num_cpus}" == "" ]; then
		echo "coverage.sh: number of CPUs has to be an intenger greater than 1"
		exit 1
	fi
	if ! pip freeze | grep pytest-xdist; then
		echo 'coverage.sh: pytest-xdist needs to be installed to use multiple CPUS'
		exit 1
	fi
	noption="-n ${num_cpus}"
fi


# Processing
cd ${src_dir}
${pkg_dir}/sbin/coveragerc-manager.py 'local' 1 ${pkg_dir} ${module}
py.test -x -s -vv ${noption} --cov-config ${pkg_dir}/.coveragerc_local --cov ${pkg_dir}/putil/ --cov-report html ${file}
${pkg_dir}/sbin/coveragerc-manager.py 'local' 0 ${pkg_dir}
rm -rf ${pkg_dir}/putil/.coverage
cd ${cpwd}
