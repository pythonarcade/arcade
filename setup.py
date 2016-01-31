VERSION = "0.0.6"
RELEASE = VERSION + "a4"

#!/usr/bin/env python
import os
import sys
import distutils.sysconfig
from setuptools import setup

if __name__ == "__main__":

    if "--format=msi" in sys.argv or "bdist_msi" in sys.argv:
        # hack the version name to a format msi doesn't have trouble with
        VERSION = VERSION.replace("-alpha", "a")
        VERSION = VERSION.replace("-beta", "b")
        VERSION = VERSION.replace("-rc", "r")

    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.rst")
    readme = open(fname, "r")
    long_desc = readme.read()
    readme.close()


    setupdata = {
        "name":  "arcade",
        "version": RELEASE,
        "description": "Arcade Game Development Library",
        "long_description": long_desc,
        "author": "Paul Vincent Craven",
        "author_email": "paul.craven@simpson.edu",
        "license": "Public Domain / zlib",
        "url": "http://arcade.academy",
        "download_url": "http://arcade.academy",
        "packages": ["arcade",
                     "arcade.key",
                     "arcade.color"
                     ],
        "classifiers": [
            "Development Status :: 1 - Planning",
            "Intended Audience :: Developers",
            "License :: Public Domain",
            "License :: OSI Approved :: zlib/libpng License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Software Development :: Libraries :: Python Modules",
            ],
        "test_suite": "tests",
        "data_files": [(distutils.sysconfig.get_python_lib(), ["dlls/avbin.dll"])],
        }
    setup(**setupdata)
