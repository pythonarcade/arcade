#!/bin/bash

rm -rf doc/build
rm dist/*
python3 setup.py clean
python3 setup.py build
python3 setup.py bdist_wheel
pip3 uninstall -y arcade
for file in dist/*
do
  pip install $file
done
