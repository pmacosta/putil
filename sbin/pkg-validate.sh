#!/bin/bash
# pkg-validate.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "pkg-validate.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  pkg-validate.sh [-h] [-n num-cpus]\n" >&2
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
			echo "pkg-validate.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	echo "pkg-validate.sh: too many command line arguments" >&2
	exit 1
fi

# Argument validation
export NOPTION=""
if [ "${num_cpus}" != "" ]; then
	num_cpus=$(echo "${num_cpus}" | grep "^[2-9][0-9]*$")
	if [ "${num_cpus}" == "" ]; then
		echo "pkg-validate.sh: number of CPUs has to be an intenger greater than 1"
		exit 1
	fi
	if ! pip freeze | grep pytest-xdist; then
		echo 'pkg-validate.sh: pytest-xdist needs to be installed to use multiple CPUS'
		exit 1
	fi
	export NOPTION="-n ${num_cpus}"
fi

# Processing
cd ${pkg_dir}
tox -e py27
tox -e docs
export NOPTION=""
cd ${cpwd}
