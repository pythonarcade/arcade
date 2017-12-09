rem This does a fast build and install, but no unit tests

python setup.py build
python setup.py bdist_wheel
pip uninstall -y arcade
for /r %%i in (dist\*) do pip install "%%i"
