#!/usr/bin/env python
import sys
from setuptools import setup

if sys.platform == "darwin":
    required_python_version=">=3.6,<3.9"
else:
    required_python_version=">=3.6"

exec(open("arcade/version.py").read())
setup(python_requires=required_python_version,
      version=VERSION)
