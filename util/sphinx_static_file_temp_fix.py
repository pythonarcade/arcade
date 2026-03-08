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

import shutil
import sys
import logging
from pathlib import Path

FILE = Path(__file__)
UTIL_DIR = FILE.parent.resolve()
REPO_ROOT = UTIL_DIR.parent.resolve()

# Ensure we get utility & Arcade imports first
sys.path.insert(0, str(REPO_ROOT))

log = logging.getLogger(str(FILE.relative_to(REPO_ROOT)))

DOC_DIR = REPO_ROOT / "doc"

ENABLE_DEVMACHINE_SPHINX_STATIC_FIX = REPO_ROOT / ".ENABLE_DEVMACHINE_SPHINX_STATIC_FIX"

BUILD_ROOT = REPO_ROOT / "build"
BUILD_HTML_DIR = BUILD_ROOT / "html"

SOURCE_STATIC_DIR = DOC_DIR / "_static"
BUILD_STATIC_DIR = BUILD_HTML_DIR / "_static"

BUILD_CSS_DIR = BUILD_STATIC_DIR / "css"
SOURCE_CSS_DIR = SOURCE_STATIC_DIR / "css"

BUILD_JS_DIR = BUILD_STATIC_DIR / "js"
SOURCE_JS_DIR = SOURCE_STATIC_DIR / "js"

force_copy_on_change: dict[Path, Path] = {  # pending: sphinx >= 8.1.4
    # You can add per-dir config the lazy way:
    # 1. copy & paste this block
    # 2. modifying it with filtering
    **{source_file: BUILD_CSS_DIR / source_file.name for source_file in SOURCE_CSS_DIR.glob("*.*")},
    **{source_file: BUILD_JS_DIR / source_file.name for source_file in SOURCE_JS_DIR.glob("*.*")},
}


# pending: some clever use of util/doc_helpers/vfs.py
def force_sync(src: Path, dest: Path, dry: bool = False) -> None:
    """Sync a single file from ``src`` to ``dest``.

    Caveats:

    1. Assumes both are `pathlib.Path` instances
    2. Assumes both are small
    3. Fails hard when a file isn't found

    """

    try:
        if src.read_text() == dest.read_text():
            log.info(f"   SKIP: {src} is current!")
        elif dry:
            log.info(f"   DRY : {src} was out of date, but dry run left it as-is!")
        else:
            log.info(f"   SYNC: {src} was out of date!")
            shutil.copyfile(src, dest)
    except Exception as e:
        log.error(f"   FAIL: {src} failed: {e}")
        raise e


def main():
    skip_reason = None

    if not ENABLE_DEVMACHINE_SPHINX_STATIC_FIX.exists():
        skip_reason = (
            f"SKIP: Force sync not enabled by a {ENABLE_DEVMACHINE_SPHINX_STATIC_FIX} file!"
        )
    elif not BUILD_HTML_DIR.exists():
        skip_reason = f"SKIP: {BUILD_HTML_DIR} does not exist yet."

    if skip_reason is not None:
        log.info(" " + skip_reason)
    else:
        # indented so we can grep for Done force-syncing in the logs
        from sphinx import __version__ as sphinx_version

        log.info(f" SYNC: Force-sync enable file found and build-dir exists")
        if sphinx_version >= "8.1.4":
            log.warning(
                " Sphinx >= 8.1.4 may patch broken _static copy\n"
                "  (see https://github.com/sphinx-doc/sphinx/issues/1810)"
            )

        for src, dest in force_copy_on_change.items():
            force_sync(src, dest)

    log.info(" Done force-syncing.")


if __name__ == "__main__":
    main()
