#!/bin/bash

python3 doc/source/preprocess_files.py
sphinx-build -b html doc/source doc/build/html
