#!/usr/bin/env python

from os import path
import sys
from setuptools import setup

BUILD = 0
VERSION = "2.0.0b4"
RELEASE = VERSION

if __name__ == "__main__":

    if "--format=msi" in sys.argv or "bdist_msi" in sys.argv:
        # hack the version name to a format msi doesn't have trouble with
        VERSION = VERSION.replace("-alpha", "a")
        VERSION = VERSION.replace("-beta", "b")
        VERSION = VERSION.replace("-rc", "r")

    fname = path.join(path.dirname(path.abspath(__file__)), "README.rst")
    with open(fname, "r") as f:
        long_desc = f.read()

    setup(
          name="arcade",
          version=RELEASE,
          description="Arcade Game Development Library",
          long_description=long_desc,
          author="Paul Vincent Craven",
          author_email="paul.craven@simpson.edu",
          license="MIT",
          url="http://arcade.academy",
          download_url="http://arcade.academy",
          install_requires=[
            'pyglet==1.4.0b1',
            'pillow',
            'numpy'
          ],
          packages=["arcade",
                    "arcade.key",
                    "arcade.color",
                    "arcade.csscolor",
                    "arcade.examples"
                    ],
          classifiers=[
              "Development Status :: 5 - Production/Stable",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: MIT License",
              "Operating System :: OS Independent",
              "Programming Language :: Python",
              "Programming Language :: Python :: 3.6",
              "Programming Language :: Python :: 3.7",
              "Programming Language :: Python :: Implementation :: CPython",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
          test_suite="tests",
          package_data={'arcade': ['examples/images/*.png',
                                   'examples/images/character_sprites/*.png',
                                   'examples/images/explosion/*.png',
                                   'examples/images/isometric_dungeon/*.png',
                                   'examples/images/*.jpg',
                                   'examples/*.csv',
                                   'examples/*.tmx',
                                   'examples/sounds/*']},
          data_files=[("lib/site-packages/arcade/Win32", ["Win32/avbin.dll"]),
                      ("lib/site-packages/arcade/Win64", ["Win64/avbin.dll"]),
                      ("lib/python3.6/site-packages/lib/site-packages/arcade/lib", ["lib/libavbin.10.dylib"])]
         )
