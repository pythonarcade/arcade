# Contributing to Arcade

Arcade welcomes contributions, including:

* [Bug reports & feature suggestions](https://github.com/pythonarcade/arcade/issues)
* Bug fixes
* Implementations of requested features
* Corrections & additions to the documentation 
* Improvements to the tests

## Before Making Changes 

Before working on an improvement, please 
[open an issue](https://github.com/pythonarcade/arcade/issues) if one
does not already exist for it. 

After you finish your changes, you should do the following:
1. Test them locally
2. Submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests)
from your fork to Arcade's development branch.

## Requirements 

This guide assumes you've already done the following:
1. [Installed `python` with `pip`](https://wiki.python.org/moin/BeginnersGuide/Download)
2. [Installed git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
3. [Forked the repo on GitHub](https://docs.github.com/en/get-started/quickstart/fork-a-repo#forking-a-repository) 
4. [Cloned your fork locally](https://docs.github.com/en/get-started/quickstart/fork-a-repo#cloning-your-forked-repository)
5. Changed into your local clone in the terminal

[Creating & using a virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)
is also strongly recommended.

## Installing Arcade in Editable Mode

To install all necessary project dependencies, run this command in your
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

To run the framework's automated tests, use the following command.

```shell
pytest --ignore=tests/test_examples
```

### Building & Testing Documentation

You can build documentation locally using the following steps.

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

Open [http://localhost:8000](http://localhost:8000) in your browser to
browse & preview the doc.

Be sure to re-run build & refresh to update after making changes!
