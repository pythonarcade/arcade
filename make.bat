rem This builds the project, installs it, and runs unit tests

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
python doc/preprocess_files.py
sphinx-build -b html doc doc/build/html

rem Run tests and do code coverage
coverage run --source arcade setup.py test
coverage report -m
