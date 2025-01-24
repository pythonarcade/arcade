# Release Checklist

1. Check for updated libraries, and if we need to pin a more recent version.
2. Run `ruff arcade`
3. Run `mypy arcade`
4. In docs folder, type `make clean` then  `make html` and confirm no warnings/errors.
5. Run unit tests in `tests` folder.
6. Run `tests/test_examples/run_all_examples.py`
7. Make sure `arcade/examples/asteroid_smasher.py` is playable.
8. Make sure `arcade/examples/platform_tutorial/17_views.py` is playable.
9. Update version number in `arcade/version.py`
10. Update :ref:`release_notes` with release dates and any additional
   info needed.
11. Make sure last check-in ran clean on GitHub actions, viewable on Discord
12. Merge development branch into maintenance.
13. Add label to release
14. Push code. Check for "clean compile on GitHub.
15. Run "Distribute built to PyPi Production" (See below for manual deployment)
18. Confirm release notes appear on website.
19. Announce on Arcade Discord, Python Discord, Reddit Python Arcade, etc.

## Manual Deployment

1. Type `make clean`
2. Type `make dist`
3. Type `make deploy_pypi`
