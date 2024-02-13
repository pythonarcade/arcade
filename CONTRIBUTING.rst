Contributing to Arcade
======================

Arcade welcomes contributions, including:

* `Bug reports & feature suggestions <https://github.com/pythonarcade/arcade/issues>`_
* Bug fixes
* Implementations of requested features
* Corrections & additions to the documentation 
* Improvements to the tests

If you're looking for a way to contribute, try checking
`the currently active issues <https://github.com/pythonarcade/arcade/issues>`_
for one that needs work.

Before Making Changes
---------------------

Before working on an improvement, please make sure to
`open an issue <https://github.com/pythonarcade/arcade/issues>`_ if one
does not already exist for it.

Tips:

1. Try to keep individual PRs to reasonable sizes
2. If you want to make large changes, please discuss them with Arcade's developers beforehand

Discussion can happen in a GitHub issue's comments or on `Arcade's Discord server <https://discord.gg/ZjGDqMp>`_.

After Making Changes
--------------------

After you finish your changes, you should do the following:

1. Test your changes according to the :ref:`Testing` section below
2. Submit a
   `pull request <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests>`_
   from your fork to Arcade's development branch.

The rest of the guide will help you get to this point & explain how to test in more detail.

Requirements
------------

Although using arcade only requires Python 3.8 or higher, development
currently requires 3.9 or higher.

The rest of this guide assumes you've already done the following:

1. `Installed Python 3.9+ with pip <https://wiki.python.org/moin/BeginnersGuide/Download>`_
2. `Installed git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_
3. `Forked the repo on GitHub <https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository>`_
4. `Cloned your fork locally <https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository>`_
5. Changed directories into your local Arcade clone's folder

`Creating & using a virtual environment <https://docs.python.org/3/library/venv.html#creating-virtual-environments>`_
is also strongly recommended.

Installing Arcade in Editable Mode
----------------------------------

To install all necessary development dependencies, run this command in your
terminal from inside the top level of the arcade directory:

.. code-block:: shell

    # For Unix-like shells (Linux, macOS)
    pip install -e '.[dev]'

.. code-block:: shell

    # For Windows
    pip install -e .[dev]

If you get an error like the one below, you probably need to update your pip version:

.. code-block:: text

    ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /home/user/Projects/arcade
    (A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)

Upgrade by running the following command:

.. code-block:: shell

    pip install --upgrade pip

Mac & Linux users can improve their development experience further by following the optional
steps at the end of this document.

.. _testing:

Testing
-------

You should test your changes locally before submitting a pull request
to make sure they work correctly & don't break anything.

Ideally, you should also write unit tests for new features. See the tests folder
in this repo for current tests.

Testing Code Changes
^^^^^^^^^^^^^^^^^^^^

First, run the below command to run our linting tools automatically. This will run Mypy
and Ruff against Arcade. The first run of this may take some as MyPy will not have any
caches built up. Sub-sequent runs will be much faster.

.. code-block:: shell

    python make.py lint

If you want to run either of these tools individually, you can do

.. code-block:: shell

    python make.py ruff

or 

.. code-block:: shell

    python make.py mypy

Now you run the framework's unit tests with the following command:

.. code-block:: shell

    python make.py test

Building & Testing Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Automatic Rebuild with Live Reload
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can build & preview documentation locally using the following steps.

Run the doc build to build the web page files, and host a webserver to preview:

.. code-block:: shell

    python make.py serve

You can now open `http://localhost:8000 <http://localhost:8000>`_ in your browser to preview the docs.

The ``doc/build/html`` directory will contain the generated website files.  When you change source files,
it will automatically regenerate, and browser tabs will automatically refresh to show your updates.

If you suspect the automatic rebuilds are failing to detect changes, you can
run a simpler one-time build using the following instructions.

.. _how-to-compile:

One-time build
~~~~~~~~~~~~~~

Run the doc build to build the web page files:

.. code-block:: shell

    python make.py html

The ``doc/build/html`` directory will contain the generated website files.

Start a local web server to preview the doc:

.. code-block:: shell

    python -m http.server -d doc/build/html

You can now open `http://localhost:8000 <http://localhost:8000>`_ in your browser to preview the doc.

Be sure to re-run build & refresh to update after making changes!

Optional: Improve Ergonomics on Mac and Linux
---------------------------------------------

make.py shorthand
^^^^^^^^^^^^^^^^^

On Mac & Linux, you can run the make script as ``./make.py`` instead of ``python make.py``.

For example, this command:

.. code-block:: shell

    python make.py lint

can now be run this way:

.. code-block:: shell

    ./make.py lint

Enable Shell Completions
^^^^^^^^^^^^^^^^^^^^^^^^

On Mac & Linux, you can enable tab completion for commands on the following supported shells:

* ``bash`` (the most common default shell)
* ``zsh``
* ``fish``
* ``powershell``
* ``powersh``

For example, if you have typed the following...

.. code-block:: shell

    ./make.py h

Tab completion would allow you to press tab to auto-complete the command:

.. code-block:: shell

    ./make.py html

Note that this may interfere if you work on other projects that also have a `make.py` file.

To enable this feature, most users can follow these steps:

1. Run ``./make.py whichshell`` to find out what your default shell is
2. If it is one of the supported shells, run ``./make.py --install-completion $(basename "$SHELL")``
3. Restart your terminal

If your default shell is not the shell you prefer using for arcade development,
you may need to specify it to the command above directly instead of using
auto-detection.
