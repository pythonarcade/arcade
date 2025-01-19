#!/usr/bin/env python3
"""
A quick, ugly fix for a broken static file handler.

This runs sync over static folders entries crucial for web dev
which Sphinx <= 8.1.3 does not properly handle due to early exit
checks. Keep the following in mind:

1. It is not tested to work with sphinx-autobuild or ./make.py serve
2. It was created for use with Arcade' ./make.py html

To enable it on your system:

1. cd to your repo root
2. `touch  .ENABLE_DEVMACHINE_SPHINX_STATIC_FIX`

Removal requires:

1. Sphinx 8.1.4 or another version ships the fixes:

   * https://github.com/sphinx-doc/sphinx/pull/13236
   * https://github.com/sphinx-doc/sphinx/issues/181

2. We verify it as compatible with Arcade's dependencies


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


STATIC_CSS_DIR = STATIC_SOURCE_DIR / "css"
force_copy_on_change = {  # pending: sphinx >= 8.1.4
    source_file: BUILD_STATIC_DIR / f"css/{source_file.name}"
    for source_file in STATIC_CSS_DIR.glob("*.css")
}

def force_sync(src, dest, dry: bool = False):
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
    elif BUILD_HTML_DIR.exists():
        log.info(f"SYNC: Force-sync enable file found")
        for src, dest in force_copy_on_change.items():
            force_sync(src, dest)
    else:
        log.info("Skipping force-sync due to no build dir")


if __name__ == "__main__":
    main()
