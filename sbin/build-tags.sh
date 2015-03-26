#!/bin/bash
# build-tags.sh
# Copyright (c) 2013-2015 Pablo Acosta-Serafini
# See LICENSE for details

print_usage_message () {
	echo -e "build-tags.sh\n" >&2
	echo -e "Usage:" >&2
	echo -e "  build-tags.sh [-h]\n" >&2
	echo -e "Options:" >&2
	echo -e "  -h  Show this screen" >&2
}

# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "$source" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "$source" )" && pwd )"
	source="$(readlink "$source")"
	[[ $source != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "$source" )" && pwd )"
package_root=$(dirname ${dir})
package_name=$(basename ${package_root})

# Read command line options
while getopts ":h" opt; do
	case ${opt} in
		h)
			print_usage_message
			exit 0
			;;
		\?)
			echo "build-tags.sh: invalid option" >&2
			print_usage_message
			exit 1
			;;
	esac
done
shift $((${OPTIND} - 1))
if [ "$#" != 0 ]; then
	echo "build-tags.sh: too many command line arguments" >&2
	exit 1
fi

ctags -V --tag-relative -f $package_root/tags -R $package_root/${package_name}/*.py $package_root/tests/*.py
# */2 * * * * /proj/ad9625_e_expctl/sos_pacosta/pacosta/sim/bin/build_tags.sh &>/home/pacosta/log/cheetah_tags.log
