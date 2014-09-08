#!/bin/bash

src_dir=$HOME/python/putil/src/putil
# Default values for command line options
rebuild=0

# Read command line options
while getopts "r --long rebuild" opt; do
	case $opt in
		r|rebuild)
			rebuild=1
			;;
		\?)
			echo 'Invalid option: $OPTARG' >&2
			;;
	esac
done

if [ $rebuild == 1 ]; then
	echo 'Rebuilding exceptions documentation'
	modules=(pcsv)
	for module in ${modules[@]}; do
		module_file="$src_dir"/"$module".py
		echo '   Processing module '$module_file
		cog.py -e -x -r $module_file > /dev/null
		cog.py -e -r $module_file > /dev/null
	done
fi
echo ' '

make html
