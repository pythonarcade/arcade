.. _release_checklist:

Release Checklist
=================

#. Check for updated libraries, and if we need to pin a more recent version.
#. Run ``flake8 arcade``
#. Run ``mypy arcade``
#. In docs folder, type  ``make clean`` then  ``make html`` and confirm no warnings/errors.
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
#. Push code. Check for clean compile on github.
#. Type ``make clean``
#. Type ``make dist``
#. Type ``make deploy_pypi``
#. Confirm release notes appear on website.
#. Announce on Arcade Discord, Python Discord, Reddit Python Arcade, etc.