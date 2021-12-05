@echo off

rem Build script for Windows

IF "%~1"=="" GOTO printdoc
IF "%~1"=="full" GOTO makefull
IF "%~1"=="dist" GOTO makedist
IF "%~1"=="test" GOTO test
IF "%~1"=="testcov" GOTO test
IF "%~1"=="typecheck" GOTO typecheck
IF "%~1"=="fast" GOTO makefast
IF "%~1"=="docs" GOTO makedoc
IF "%~1"=="spelling" GOTO spelling
IF "%~1"=="deploy_pypi" GOTO deploy_pypi
IF "%~1"=="deploy_docs" GOTO deploy_docs
IF "%~1"=="clean" GOTO clean
GOTO printdoc

:clean

rmdir /S /Q arcade.egg-info
rmdir /S /Q build
rmdir /S /Q dist
rmdir /S /Q .pytest_cache
rmdir /S /Q doc\build

GOTO end

:test

pytest
GOTO end

:testcov

pytest --cov=arcade
GOTO end

:typecheck

echo Running mypy type checker:
mypy -p arcade
IF ERRORLEVEL 1 (
    echo ERROR: Type checking via mypy found errors, detailed above.
) else (
    echo OK: Type checking via mypy found no errors.
)
GOTO end

:makedist

rem Clean out old builds
del /q dist\*.*
python setup.py clean

rem Build the python
python setup.py build
python setup.py bdist_wheel

GOTO end

:makefull
rem -- This builds the project, installs it, and runs unit tests

rem Clean out old builds
rmdir /s /q "doc\build"
del /q dist\*.*
python setup.py clean

rem Build the python
python setup.py build
python setup.py bdist_wheel

rem Install the packages
pip uninstall -y arcade
for /r %%i in (dist\*) do pip install "%%i"

rem Build the documentation
sphinx-build -b html doc doc/build/html

rem Run tests and do code coverage
coverage run --source arcade setup.py test
coverage report --omit=arcade/examples/* -m

GOTO end

rem == This does a fast build and install, but no unit tests

:makefast

python setup.py build
python setup.py bdist_wheel
pip uninstall -y arcade
for /r %%i in (dist\*) do pip install "%%i"

GOTO end

rem -- Deploy

:deploy_pypi
rem Do a "pip install twine" and set environment variables before running.

twine upload -u %PYPI_USER% -p %PYPI_PASSWORD% -r pypi dist/*

GOTO end

rem -- Print documentation

:printdoc

echo make test        - Runs the tests
echo make testcov     - Runs the tests with coverage
echo make dist        - Make the distributables
echo make deploy_pypi - Deploy to PyPi (if you have environment
echo                    variables set up correctly.)
:end