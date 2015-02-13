#!/bin/bash
# Find directory where script is (from http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in)
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
	DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
	SOURCE="$(readlink "$SOURCE")"
	[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
repo_dir=$(dirname ${DIR})

cpwd=${PWD}
git_hooks_dir=${repo_dir}/.git/hooks
hooks=(pre-commit)
cd ${git_hooks_dir}
for hook in ${hooks[@]}; do
	ln -s -f ${DIR}/${hook} ${hook}
done
cd ${cpwd}
