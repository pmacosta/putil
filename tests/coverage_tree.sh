#!/bin/bash
cd ../putil
py.test --cov putil.tree --cov-report term-missing ../tests/test_tree.py
