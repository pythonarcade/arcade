rem rmdir /s /q "doc\build"
python doc/preprocess_files.py
sphinx-build -n -b html doc doc/build/html
