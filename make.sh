#!/bin/bash

rm -rf doc/build
rm -f dist/*
python3 -m pip install -I -e arcade
sphinx-build -b html doc doc/build/html
coverage run --source arcade setup.py test
coverage report -m
