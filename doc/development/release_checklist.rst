Release Checklist
=================

#. Check for updated libraries, and if we need to pin a more recent version.qq
#. Run ``flake8 arcade``
#. Run ``mypy arcade``
#. Run unit tests in ``tests`` folder.
#. Run ``tests/test_examples/run_all_examples.py``
#. Make sure ``arcade/examples/asteroid_smasher.py`` is playable.
#. Make sure ``arcade/examples/platform_tutorial/17_views.py`` is playable.
#. Update version number in  ``arcade/version.py``
#. Update :ref:`release_notes` with release dates and any additional
   info needed.
#. Make sure last check-in ran clean on github actions, viewable on Discord
#. Merge development branch into maintenance.
#. Add label to release
#. Type ``make clean``
#. Type ``make dist``
#. Type ``make deploy_pypi``
