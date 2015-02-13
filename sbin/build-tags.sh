#!/bin/bash
# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
source="${BASH_SOURCE[0]}"
while [ -h "$source" ]; do # resolve $source until the file is no longer a symlink
	dir="$( cd -P "$( dirname "$source" )" && pwd )"
	source="$(readlink "$source")"
	[[ $source != /* ]] && source="$dir/$source" # if $source was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
dir="$( cd -P "$( dirname "$source" )" && pwd )"
export PACKAGE_ROOT=$(dirname ${dir})
ctags -V --tag-relative -f $PACKAGE_ROOT/tags -R $PACKAGE_ROOT/putil/*.py $PACKAGE_ROOT/tests/*.py
# */2 * * * * /proj/ad9625_e_expctl/sos_pacosta/pacosta/sim/bin/build_tags.sh &>/home/pacosta/log/cheetah_tags.log
