"""
Helpers for dealing with the real-world file system.

"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Generator, TypeVar, Hashable, Iterable, Mapping, Sequence, Callable
import logging

H = TypeVar('H', bound=Hashable)

FILE = Path(__file__)
REPO_ROOT = Path(__file__).parent.parent.resolve()
log = logging.getLogger(str(FILE.relative_to(REPO_ROOT)))


def dest_older(src: Path | str, dest: Path | str) -> bool:
    """True if ``dest`` is older than ``src``.

    This works because git does not bother syncing the modified times
    on files. It delegates that data to the commit history.

    Args:
         src: A str or :py:class:`pathlib.Path`.
         dest: A str or :py:class:`pathlib.Path`.
    """
    return Path(src).stat().st_mtime > dest.stat().st_mtime


def multi_glob(
        p: str | Path,
        *globs: str,
        predicate: Callable[[Path], bool] | None = None
) -> Generator[Path, None, None]:
    """Chain multiple :py:class:`pathlib.Path.glob` results into one.

    The
    Args:
        p: the path to merge glob args for
        globs: The glob strings to use.
        predicate: An optional filter predicate.
    Yields:
        A series of paths with possible duplicates.
    """
    p = Path(p)
    for glob in globs:
        if predicate:
            yield from filter(predicate, p.glob(glob))
        else:
            yield from p.glob(glob)


def unique(items: Iterable[H], seen: set | None = None) -> Generator[H, None, None]:
    """Filter hashable ``items`` by adding them to a ``seen`` set during iteration.

    Passing a re-used set in allows efficiently visiting nodes.

    Args:
        items: An iterable of hashables to reject duplicates from.
        seen: specify a set rather than creating a new one for this call.
    """
    if seen is None:
        seen = set()
    for new in (elt for elt in items if elt not in seen):
        seen.add(new)
        yield new


def sync_dir(src_dir: Path, dest_dir: Path, *globs: str, done: set | None = None) -> None:
    """Sync a directory's files by using :py:mod:`pathlib` style ``globs``.

    Args:
        src_dir: The source directory to read.
        dest_dir: Where to sync any globbed files from.
        globs: Match these and sync them into ``dest_dir``.
        done: Pass a set of visited paths to enforce custom uniqueness.
    """
    if not src_dir.is_dir():
        raise ValueError(f"source is not a directory: {src_dir}")
    if dest_dir.is_file():
        raise ValueError(f"dest dir is not a directory: {dest_dir}")
    for src_file in unique(multi_glob(src_dir, *globs), seen=done):
        dest_file = dest_dir / src_file.name

        if not dest_file.exists() or dest_older(src_file, dest_file):
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            log.info(f' Copying media file {src_file} to {dest_file}')

            shutil.copyfile(src_file, dest_file)


def copy_media(
        src_root: Path | str,
        dest_root: Path | str,
        items: Mapping[str | Path, Sequence[str]],
        done: set | None = None
) -> None:
    """A more configurable version of the file syncing scripts we use.

    Args:
        src_root: Where to start looking for matching ``items``
        dest_root: Where to write the new items.
        items: A mapping of folder names to glob sequences.
        done: A set to use as a uniqueness check, if any.
    """

    if done is None:
        done = set()
    logging.info("")
    for dir_name, sub_items in items.items():
        print(f"    Copying... {' '.join(map(repr, sub_items))}...")

        src_sub = (src_root / dir_name).resolve()
        dest_sub = dest_root / dir_name
        print("       from :", src_sub)
        print("       to   :", dest_sub)
        sync_dir(src_sub, dest_sub, *items, done=done)
