#!/bin/bash

src_dir = $HOME/python/putil/src/putil/
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
	echo 'Rebuilding exception documentation'
	modules=(pcsv.py)
	for module in ${modules[@]}; do
		echo '   Processing module '$module
		cog.py -r "$src_dir"/"$module".py
	done
fi
echo ' '

make html
