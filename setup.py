#!/usr/bin/env python
from setuptools import setup

exec(open("arcade/version.py").read())
setup(version=VERSION)
