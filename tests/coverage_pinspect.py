#!/bin/bash
cd ../putil
py.test --cov putil.pinspect --cov-report term-missing ../tests/test_pinspect.py
