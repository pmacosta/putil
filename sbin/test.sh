#!/bin/bash

print_usage_message () {
	echo -e "test.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  test.sh [-h] [module-name] [test-name]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
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
while getopts ":h" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		\?)
			echo "test.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" == 0 ]; then
	echo "test.sh: no module to run a test bench on" >&2
	exit 1
fi
if [ "$#" -gt 2 ]; then
	echo "test.sh: too many command line arguments" >&2
	exit 1
fi

# Argument validation
module=$1
file=${pkg_dir}/tests/test_${module}.py
if [ ! -f "${file}" ]; then
	echo "test.sh: test bench for module ${module} could not be found"
	exit 1
fi

# Processing
cd ${pkg_dir}/tests
sta=""
if [ "${2}" != "" ]; then
	sta="-k ${2}"
fi
py.test -s -vv -x ${sta} test_${1}.py
cd ${cpwd}
