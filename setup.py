#!/usr/bin/env python
import sys
from os import path

from setuptools import find_namespace_packages, setup

if sys.platform == "darwin":
    required_python_version = ">=3.6"
else:
    required_python_version = ">=3.6"

exec(open("arcade/version.py").read())


def get_long_description() -> str:
    fname = path.join(path.dirname(path.abspath(__file__)), "README.rst")
    with open(fname, "r") as f:
        return f.read()


setup(
    name="arcade",
    description="Arcade Game Development Library",
    long_description=get_long_description(),
    author="Paul Vincent Craven",
    author_email="paul.craven@simpson.edu",
    license="MIT",
    url="https://arcade.academy",
    download_url="https://arcade.academy",
    install_requires=[
        "pyglet==2.0.dev4",
        "pillow~=8.3",
        "pymunk~=6.0.0",
        "pyyaml~=5.4",
        "shapely==1.7.1",
        "pytiled-parser==1.5.0",
        "dataclasses; python_version < '3.7'",
    ],
    extras_require={
        "dev": [
            "pytest",
            "flake8",
            "mypy",
            "coverage",
            "coveralls",
            "pytest-mock",
            "pytest-cov",
            "sphinx",
            "sphinx-sitemap",
            "sphinx_rtd_theme",
            "sphinx_copybutton",
            "dirsync",
            "wheel",
            "numpy",
        ],
    },
    packages=find_namespace_packages(
        include=["arcade", "arcade.*"],
        exclude=[],
    ),
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    project_urls={
        "Documentation": "https://arcade.academy/",
        "Example Code": "https://arcade.academy/examples/index.html",
        "Issue Tracker": "https://github.com/pythonarcade/arcade/issues",
        "Source": "https://github.com/pythonarcade/arcade",
        "On-line Book": "https://learn.arcade.academy",
    },
    version=VERSION
)
