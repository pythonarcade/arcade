del C:\Python35\Lib\site-packages\arcade*.egg
python setup.py clean
python setup.py build
python setup.py install
sphinx-build -b html doc/source doc/build/html
python setup.py test