# Contributing to Arcade

Arcade welcomes contributions, including:

* [Bug reports & feature suggestions](https://github.com/pythonarcade/arcade/issues)
* Bug fixes
* Implementations of requested features
* Corrections & additions to the documentation 
* Improvements to the tests

If you're looking for a way to contribute, try checking [the currently active issues](https://github.com/pythonarcade/arcade/issues)
for one that needs work.

## Before Making Changes 

Before working on an improvement, please make sure to
[open an issue](https://github.com/pythonarcade/arcade/issues) if one
does not already exist for it.

Tips:
1. Try to keep individual PRs to reasonable sizes
2. If you want to make large changes, please discuss them with Arcade's developers beforehand

Discussion can happen in a GitHub issue's comments or on [Arcade's Discord server](https://discord.gg/ZjGDqMp).

## After Making Changes

After you finish your changes, you should do the following:
1. Test your changes with Arcade's test suite as well as `mypy` & `flake8`
2. Submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests)
from your fork to Arcade's development branch.

The rest of the guide will help you get to this point.

## Requirements 

This guide assumes you've already done the following:
1. [Installed `python` with `pip`](https://wiki.python.org/moin/BeginnersGuide/Download)
2. [Installed git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
3. [Forked the repo on GitHub](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) 
4. [Cloned your fork locally](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
5. Changed directories into your local arcade clone's folder

[Creating & using a virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
is also strongly recommended.

## Installing Arcade in Editable Mode

To install all necessary development dependencies, run this command in your
terminal from inside the top level of the arcade directory:

```shell
pip install -e .[dev]
```

## Testing

You should test your changes locally before submitting a pull request
to make sure they work correctly & don't break anything.

Ideally, you should also write unit tests for new features. See the tests folder
in this repo for current tests.

### Testing Code Changes

First, run `mypy` and `flake8` from inside the arcade folder. You should fix
any issues they report.

Then run the framework's automated tests with the following command:

```shell
pytest --ignore=tests/test_examples
```

### Building & Testing Documentation

You can build & preview documentation locally using the following steps.

Change into the doc directory:
```commandline
cd doc
```

Run the doc build to build the web page files:
```commandline
make html
```
The `build/html` directory will contain the generated website files.

Start a local web server to preview the doc:
```commandline
python -m http.server -d build/html
```

You can now open [http://localhost:8000](http://localhost:8000) in your browser to preview the doc.

Be sure to re-run build & refresh to update after making changes!