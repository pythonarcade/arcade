Contributing to Arcade
======================

Suggest Improvements
--------------------

Open up issues:

https://github.com/pythonarcade/arcade/issues

Fix Bugs or Implement Features
------------------------------

Before you code, please open an issue for what you are coding, and then
check in code with that issue number (like "issue #146") as part of the
comments.

Improve the Documentation
-------------------------

You can also suggest improvements to the documentation. All the documentation
is in the codebase.

Improve Test Cases
------------------

Improving code coverage, and making better test case examples is appreciated.

How to test changes locally
---------------------------

This guide assumes you already have `python` and `pip` installed, and you have
already cloned this repository using `git`.  This guide
does not explain how to create a venv, but a venv is recommended if you already
know how to create one.

To install all necessary project dependencies, run this command in your
terminal:

```shell
pip install -e .[dev]
```

To run automated tests:

```shell
pytest --ignore=tests/test_examples
```

How to Build
------------

In the root directory of the project, you should be able to type:

* `make full` (for Windows)
* `sudo ./make.sh` (for Linux)

This will build the project, install it, and run all of the tests.
