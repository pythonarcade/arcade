# Contributing to Arcade

Arcade welcomes contributions, including:

* [Bug reports & feature suggestions](https://github.com/pythonarcade/arcade/issues)
* Bug fixes
* Implementations of requested features
* Corrections & additions to the documentation
* Improvements to the tests

If you're looking for a way to contribute, try checking
[the currently active issues](https://github.com/pythonarcade/arcade/issues)
for one that needs work. If you're new to programming or contributing, check for the
label `good first issue`, these are issues that have been identified as good candidates for first time contributors.

Notifying us about issues in the code and documentation is also a valuable contribution.

## Before Making Changes

Before working on an improvement, please make sure to
[open an issue](https://github.com/pythonarcade/arcade/issues/new) if one
does not already exist for it.

Tips:

1. Try to keep individual PRs to reasonable sizes
2. If you want to make large changes, please discuss them with Arcade's developers beforehand

Discussion can happen in a GitHub issue's comments or on [Arcade's Discord server](https://discord.gg/ZjGDqMp).

## After Making Changes

After you finish your changes, you should do the following:

1. Test your changes according to the [Testing](#testing) section below
2. Submit a
   [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests>)
   from your fork to Arcade's development branch.

The rest of the guide will help you get to this point & explain how to test in more detail.

## Requirements

Check that you are using a supported version of Python. Inspect the `pyproject.toml` file for the supported versions. We usually try to work with the latest stable python release.

The rest of this guide assumes you've already done the following:

1. [Installed Python 3.9+ with pip](https://wiki.python.org/moin/BeginnersGuide/Download)
2. [Installed git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
3. [Forked the repo on GitHub](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository)
4. [Cloned your fork locally](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
5. Changed directories into your local Arcade clone's folder

[Creating & using a virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
is also strongly recommended.

## Installing Arcade in Editable Mode

To install all necessary development dependencies, run this command in your
terminal from inside the top level of the Arcade directory:

```bash
pip install -e '.[dev]'
```

If you get an error like the one below, you probably need to update your pip version:

```
ERROR: File "setup.py" not found. Directory cannot be installed in editable mode: /home/user/Projects/arcade
(A "pyproject.toml" file was found, but editable mode currently requires a setup.py based build.)
```

Upgrade by running the following command:

```bash
pip install --upgrade pip
```

Mac & Linux users can improve their development experience further by following the optional
steps at the end of this document.

## Formatting

Arcade uses [Black](https://black.readthedocs.io/en/stable) for autoformatting our code.

This can be run both with our `make.py` script, as well as setup for your editor to run it automatically.
See [this link](https://black.readthedocs.io/en/stable/integrations/editors.html) for more information on
Black integration for your specific editor.

The following command will run black for you if you do not want to configure your editor to do it. It can be
a good idea to run this command when you are finished working anyway, as our CI will use this to check that
the formatting is correct.

```bash
python make.py format
```

In addition to Black, this will sort the imports using [Ruff](https://docs.astral.sh/ruff/). If you want to set up
your editor to run this, please see [this link](https://docs.astral.sh/ruff/integrations/) for more information on
Ruff integration for your specific editor.

Docstring should be formatted using [Google Style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

The minium for docstrings is covering all parameters in an `Args:` block.

```python
Args:
    width: The width of something
    height: The height of something
    title (optional): The title of something
```

* `Args:` should be used for all parameters
* `Returns:` can be used if the return value needs additional explanation outside
   the current docstring. If the return type is already clear from type annotation, it
   can be omitted.
* `Raises:` can be used if the function raises exceptions that need to be documented
* `Yields:` can be used if the function is a generator and yields values
* `Attributes:` we should try to avoid it and instead document the attributes in the code
* Types are visible in the api docs. It's not mandatory to include types in docstring,
  however, simple types like `int`, `str`, `float`, `bool` can be included.
* Using `optional` is a good way to indicate that a parameter is optional.
* Properties and attribute docs don't need a type when this is already clear from
  type or return annotation.

Attribute docstring in module or class:

```py
my_attribute_in_class_or_module: type = value
"""This is a docstring for the attribute."""
```

### Typing

Arcade is using type hints to help with code readability and maintainability.
Everything that can reasonably be typed should be typed.

In some situations, you may need to use `# type: ignore` to suppress type errors.
If this is an issue with a third-party library, the following format is preferred:

Also see [this issue](https://github.com/pythonarcade/arcade/issues/1796) for
more discussion on this topic.

```python
# type: ignore  # pending https://github.com/pyglet/pyglet/issues/843
```

This links to an issue in the third party library that is causing the type error.
This oddly specific syntax is compatible with both mypy and pyright.
See [this issue](https://github.com/pythonarcade/arcade/issues/1789) for more information.

### Use pre-commit hooks to automatically run formatting

This is not required, but can be helpful in case you forget to run the formatting command before committing your changes.

You can use `pre-commit <https://pre-commit.com/>`_ to automatically run lint, formatting and type checks against
your changes before you commit them.
To install pre-commit, run the following command:

```bash
pip install pre-commit
# or on Mac
brew install pre-commit
```

Then, run the following command to install the pre-commit hooks:

```bash
pre-commit install
```

## Testing

You should test your changes locally before submitting a pull request
to make sure they work correctly & don't break anything.

Ideally, you should also write unit tests for new features. See the tests folder
in this repo for current tests.

### Testing Code Changes

First, run the below command to run our linting tools automatically. This will run Mypy
and Ruff against Arcade. The first run of this may take some as MyPy will not have any
caches built up. Subsequent runs will be much faster.

```bash
python make.py lint
```

If you want to run either of these tools individually, you can do

```bash
python make.py ruff
```

or

```bash
python make.py mypy
```

Now you run the unit tests with the following command:

```bash
python make.py test
# Optionally use pytest directly
pytest tests/unit
```

### Building & Testing Documentation

#### Automatic Rebuild with Live Reload

You can build & preview documentation locally using the following steps.

Run the doc build to build the web page files, and host a webserver to preview:

```bash
python make.py serve
```

You can now open <http://localhost:8000> in your browser to preview the docs.

The `doc/build/html` directory will contain the generated website files.  When you change source files,
it will automatically regenerate, and browser tabs will automatically refresh to show your updates.

If you suspect the automatic rebuilds are failing to detect changes, you can
run a simpler one-time build using the following instructions.

#### One-time build

Run the doc build to build the web page files:

```bash
python make.py html
```

The `doc/build/html` directory will contain the generated website files.

Start a local web server to preview the doc:

```bash
python -m http.server -d doc/build/html
```

You can now open <http://localhost:8000> in your browser to preview the doc.

Be sure to re-run build & refresh to update after making changes!

#### Building PDFs

It is also possible to build a PDF of Arcade's documentation. This is
more complicated than the HTML doc because it requires
[LaTex](https://www.latex-project.org/), a powerful documentation
language.

##### Installing

On Linux distros based on Debian and Ubuntu, you may need to install
the following packages to build PDFs:

``console
sudo apt install latexmk
sudo apt install texlive-latex-extra
``
To reduce the large (300 MB+) install size of the second package, you
may be able to use the `--no-install-recommends` flag.

Other platforms may require different installation steps.

##### Building

Once you have LaTeX and extra required configs installed,
run the following:

```console
./make.py latexpdf
```

## Optional: Improve Ergonomics on Mac and Linux

### make.py shorthand

On Mac & Linux, you can run the make script as ``./make.py`` instead of ``python make.py``.

For example, this command:

```bash
python make.py lint
```

can now be run this way:

```bash
./make.py lint
```

### Enable Shell Completions

On Mac & Linux, you can enable tab completion for commands on the following supported shells:

* `bash` (the most common default shell)
* `zsh`
* `fish`
* `powershell`
* `powersh`

For example, if you have typed the following...

```bash
./make.py h
```

Tab completion would allow you to press tab to auto-complete the command:

```bash
./make.py html
```

Note that this may interfere if you work on other projects that also have a `make.py` file.

To enable this feature, most users can follow these steps:

1. Run `./make.py whichshell` to find out what your default shell is
2. If it is one of the supported shells, run `./make.py --install-completion $(basename "$SHELL")`
3. Restart your terminal

If your default shell is not the shell you prefer using for Arcade development,
you may need to specify it to the command above directly instead of using
auto-detection.
