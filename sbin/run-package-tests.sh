#!/bin/bash
# run-package-tests.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "run-package-tests.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  run-package-tests.sh [-h]\n" >&2
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
			echo "run-package-tests.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	echo "run-package-tests.sh: too many command line arguments" >&2
	exit 1
fi

# Processing
cd ${pkg_dir}
py.test -x -s -vv
cd ${cpwd}
