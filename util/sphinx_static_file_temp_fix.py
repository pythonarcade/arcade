#!/usr/bin/env python3
"""
Gets 3.0 out the door by temp fixing Sphinx rebuild not copying CSS.

IMPORTANT: ONLY LOCAL DEVELOPER MACHINES NEED THIS!

## Who should use this?

If `./make.py clean` seems like the only way to get `./make.py html` or
`./make.py serve` to serve your modified CSS, then yes, it's for you.

## How do I use this?

1. `cd` to the repo root
2. `touch .ENABLE_DEVMACHINE_SPHINX_STATIC_FIX`
3. `./make.py html` with working CSS change updates copying

## When should I be careful?

Keep the following in mind:

1. It is a temp fix which *seems* to work with both:

   * `./make.py html`
   * `./make.py serve`

3. No real config options other on/off via file presence

## What's Broken in Sphinx?

1. Sphinx has a long-standing bug which fails to copy static files
   https://github.com/sphinx-doc/sphinx/issues/1810

2. The fix is slated for 8.2.0 and the fix PR merged on Jan 13, 2025:
   https://github.com/sphinx-doc/sphinx/pull/13236

3. No, Arcade 3.0 **will not wait** for the following:

   1. Sphinx 3.2.0 to ship the fix for the problem
   2. Themes to become compatible
   3. Plugins to become compatible
   4. Our customizations to be tested with all of the above

"""

import sys
import logging
from pathlib import Path
from sphinx import __version__ as sphinx_version

UTIL_DIR = Path(__file__).parent.resolve()
REPO_ROOT = UTIL_DIR.parent.resolve()

# Ensure we get utility & Arcade imports first
sys.path.insert(0, str(REPO_ROOT))

log = logging.getLogger(__name__)

DOC_DIR = REPO_ROOT / "doc"
STATIC_SOURCE_DIR = DOC_DIR / "_static"

ENABLE_DEVMACHINE_SPHINX_STATIC_FIX = REPO_ROOT / ".ENABLE_DEVMACHINE_SPHINX_STATIC_FIX"

BUILD_DIR = REPO_ROOT / "build"
BUILD_HTML_DIR = BUILD_DIR / "html"
BUILD_STATIC_DIR = BUILD_HTML_DIR / "_static"
BUILD_CSS_DIR = BUILD_STATIC_DIR / "css"

STATIC_CSS_DIR = STATIC_SOURCE_DIR / "css"
force_copy_on_change = {  # pending: sphinx >= 8.1.4
    source_file: BUILD_CSS_DIR / source_file.name
    for source_file in STATIC_CSS_DIR.glob("*.css")
}


def force_sync(src: Path, dest: Path, dry: bool = False) -> None:
    """Sync a single file from ``src`` to ``dest``.

    Caveats:

    1. Assumes both are `pathlib.Path` instances
    2. Assumes both are small
    3. Fails hard when a file isn't found

    """
    if sphinx_version >= '8.1.4':
        log.warning(
            'Sphinx >= 8.1.4 may patch broken _static copy\n'
            '  (see https://github.com/sphinx-doc/sphinx/issues/1810)')
    try:
        if src.read_text() != dest.read_text():
            if dry:
                log.info(f" DRY : {src} was out of date, but dry run left it as-is!")
            # shutil.copyfile(src, dest)
            else:
                log.info(f" SYNC: {src} was out of date!")

        else:
            log.info(f" SKIP: {src} is current!")
    except Exception as e:
        log.error(f" FAIL: {src} failed: {e}")
        raise e


def main():
    if not ENABLE_DEVMACHINE_SPHINX_STATIC_FIX.exists():
        log.info(f"SKIP: Force-sync found no {ENABLE_DEVMACHINE_SPHINX_STATIC_FIX} file!")
        return
    elif not BUILD_HTML_DIR.exists():
        log.info(f"SKIP: {BUILD_HTML_DIR} does not exist yet.")
        return

    log.info(f"SYNC: Force-sync enable file found")
    for src, dest in force_copy_on_change.items():
        force_sync(src, dest)


if __name__ == "__main__":
    main()
