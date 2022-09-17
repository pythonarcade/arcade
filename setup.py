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
REQUIREMENTS_DEV = [
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

REQUIREMENTS_DOCS = [
    "Sphinx==5.1.1",
    "Pygments==2.13.0",
    "sphinx-copybutton==0.5.0",
    "sphinx-sitemap==2.2.0",
    "dirsync==2.2.5",
    "pyyaml==6.0",
    "docutils==0.19",
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
        "pyglet==2.0.dev23",
        "pillow~=9.2.0",
        "pymunk~=6.2.1",
        "pytiled-parser~=2.2.0",
    ],
    extras_require={
        "dev": REQUIREMENTS_DEV + REQUIREMENTS_DOCS,
        "docs": REQUIREMENTS_DOCS,
    },
    packages=find_namespace_packages(
        include=["arcade", "arcade.*"],
        exclude=[],
    ),
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    include_package_data=True,
        entry_points={'console_scripts': [
        'arcade = arcade.management:execute_from_command_line',
    ]},
    project_urls={
        "Documentation": "https://api.arcade.academy/",
        "Example Code": "https://api.arcade.academy/en/latest/examples/index.html",
        "Issue Tracker": "https://github.com/pythonarcade/arcade/issues",
        "Source": "https://github.com/pythonarcade/arcade",
        "On-line Book": "https://learn.arcade.academy",
    },
    version=VERSION,
)
