#!/bin/bash

modules=(pcontracts pcsv tree pinspect)
cd ../putil
for module in ${modules[@]}; do
	if ! py.test --cov putil.${module} --cov-report term-missing ../tests/test_${module}.py; then
		exit 1
	fi
done
