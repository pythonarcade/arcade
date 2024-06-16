from __future__ import annotations

from pathlib import Path

from .vfs import VirtualFile, Vfs, F


__all__ = (
    'F',
    'SharedPaths',
    'VirtualFile',
    'Vfs'
)


class SharedPaths:
    """These are often used to set up a Vfs and open files."""
    REPO_UTILS_DIR = Path(__file__).parent.parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    DOC_ROOT = REPO_ROOT / "doc"
    API_DOC_ROOT = DOC_ROOT / "api_docs"
