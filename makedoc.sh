#!/bin/bash

python3 doc/preprocess_files.py
sphinx-build -b html doc doc/build/html
