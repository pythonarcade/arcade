#!/usr/bin/env python
import sys
from os import path
from setuptools import find_namespace_packages, setup

with open("arcade/version.py") as file:
    exec(file.read())


def get_long_description() -> str:
    fname = path.join(path.dirname(path.abspath(__file__)), "README.rst")
    with open(fname, "r") as f:
        return f.read()

# Testing and code inspection tools
REQUIREMENTS_TESTS = [
    "pytest",
    "flake8",
    "mypy",
    "coverage",
    "coveralls",
    "pytest-mock",
    "pytest-cov",
]

# What is strictly needed for building docs (RTD)

# ALERT
# PYGMENTS 2.12.0 does not work as of 24-May-2022

# Doc build is on Python <= 3.11 to avoid 3.12 / cython issues:
# https://stackoverflow.com/questions/77490435/attributeerror-cython-sources
REQUIREMENTS_DOCS = [
    "Sphinx~=5.0.0",  # Apparently 4.5.X now breaks? (Sep 2024)
    "Pygments==2.10.0",
    "sphinx-copybutton==0.5.0",
    "sphinx-sitemap==2.2.0",
    "dirsync==2.2.5",
    "pyyaml==6.0",
    "docutils<0.18",
    "sphinx-sitemap",
    "furo",
    "sphinx_copybutton",
    "dirsync",
    "wheel",
]

setup(
    name="arcade",
    description="Arcade Game Development Library",
    long_description=get_long_description(),
    author="Paul Vincent Craven",
    author_email="paul.craven@simpson.edu",
    license="MIT",
    url="https://api.arcade.academy",
    download_url="https://api.arcade.academy",
    install_requires=[
        "pyglet==2.0.17",
        "pillow~=11.0.0",
        "pymunk~=6.9.0",
        "pytiled-parser==2.2.0",
    ],
    extras_require={
        "tests": REQUIREMENTS_TESTS,
        "docs": REQUIREMENTS_DOCS,
        "dev": REQUIREMENTS_TESTS + REQUIREMENTS_DOCS,
    },
    packages=find_namespace_packages(
        include=["arcade", "arcade.*"],
        exclude=[],
    ),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
    project_urls={
        "Documentation": "https://api.arcade.academy/",
        "Example Code": "https://api.arcade.academy/en/latest/examples/index.html",
        "Issue Tracker": "https://github.com/pythonarcade/arcade/issues",
        "Source": "https://github.com/pythonarcade/arcade",
        "On-line Book": "https://learn.arcade.academy",
    },
    version=VERSION,
)
