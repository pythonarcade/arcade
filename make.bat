rmdir /s /q "doc\build"
del /q dist\*.*
python setup.py clean
python setup.py build
python setup.py bdist_wheel
pip uninstall -y arcade
for /r %%i in (dist\*) do pip install "%%i"
sphinx-build -b html doc doc/build/html
coverage run --source arcade setup.py test
coverage report -m
