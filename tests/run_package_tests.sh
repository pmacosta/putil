#!/bin/bash

modules=(misc check pcontracts pcsv tree pinspect exh exdoc)
for module in ${modules[@]}; do
	if ! py.test -s -vv -x test_$module.py; then
		exit 1
	fi
done
