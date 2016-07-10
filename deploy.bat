rem Do a "pip install twine" and set environment variables before running.

twine upload -u %PYPI_USER% -p %PYPI_PASSWORD% -r pypi dist/*
