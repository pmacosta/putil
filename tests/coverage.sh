#!/bin/bash
cd ../putil
module=$1
py.test --cov putil.${module} --cov-report term-missing ../tests/test_${module}.py
