#!/bin/bash

modules=(misc eng pcontracts pcsv tree pinspect exh exdoc plot)
cd ../putil
for module in ${modules[@]}; do
	if ! py.test --cov putil.${module} --cov-report term-missing ../tests/test_${module}.py; then
		exit 1
	fi
done
