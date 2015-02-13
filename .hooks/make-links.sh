#!/bin/bash
hook_dir=../.git/hooks
hooks=(pre-commit)
cpwd=${PWD}
cd ${hook_dir}
for hook in ${hooks[@]}; do
	ln -s -f ${cpwd}/${hook} ${hook}
done
cd ${cpwd}
