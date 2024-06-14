"""Virtual filesystem to prevent infinite sphinx rebuild loops.

TL;DR: Fix bad Sphinx cache busts by only writing when data would change

The helpers in this module aggregate writes to virtual files. When a
sync to disk is requested, the on-disk contents of each path are read
before writing. If the written data would be identical to the current
contents, the write operation is skipped for that file.

Normally, any change to project .rst files triggers the sphinx-autobuild
used in Arcade's ./make.py serve command. However, Arcade's doc build
generates .rst files for the items below:

* API pages
* resource listings
* A quick index file

This behavior predates our adoption of sphinx-autobuild. Since writing
is the trigger condition instead of content change, it can trigger an
infinite loop as follows:

1. Sphinx runs our auto-generation scripts
2. sphinx-autobuild detects the modification to the files
3. The process repeats infinitely

We can prevent this loop by limiting writes. This module achieves this
by reading each file before write and aborting if its contents would be
unchanged.
"""
from __future__ import annotations
import os
from contextlib import suppress, contextmanager
from io import StringIO
from pathlib import Path
from typing import Generator, Type, TypeVar, Generic


class SharedPaths:
    """These are often used to set up a Vfs and open files."""
    REPO_UTILS_DIR = Path(__file__).parent.resolve()
    REPO_ROOT = REPO_UTILS_DIR.parent
    ARCADE_ROOT = REPO_ROOT / "arcade"
    API_DOC_ROOT = REPO_ROOT / "doc/api_docs/api"




class VirtualFile:
    """Subclass these to add some magic.

    """

    def __init__(self, path: str):
        self.path = path
        self._content = StringIO()

    def include_file(self, path: Path | str) -> int:
        """Copy the path's contents into this file."""
        contents = Path(path).read_text()
        return self.write(contents)

    def write(self, str: str):
        return self._content.write(str)

    def close(self):
        pass

    def _write_to_disk(self):
        before = None
        with suppress(Exception):
            with open(self.path, "r") as f:
                before = f.read()

        content = self._content.getvalue()
        if before != content:
            print(f"Writing {self.path}")
            with open(self.path, "w") as f:
                f.write(content)


F = TypeVar('F', bound=VirtualFile)


class Vfs(Generic[F]):
    """In-memory file system with sync support.

    Intended use is as follows:

    1. Create a Vfs object
    2. For any file a build script would change:

       1. Use vfs.open("file/path/here")
       2. Use the pathlib.Path-ish methods of the file, especially write

    3. Once done, call vfs_instance.write() to sync to disk
    """

    def __init__(self, file_type: Type[F] = VirtualFile):
        self.file_type: Type[F] = file_type
        self.files: dict[str, F] = dict()
        self.files_to_delete: set[Path] = set()

    def request_culling_unwritten(self, directory: str | Path, glob: str):
        """Schedule a culling for any files in directory matching glob.

        The check will occur when Vfs.write() is called to sync its data
        to disk. Any paths in files_to_delete which weren't written to
        will then be deleted.

        Doing it this way allows us to leave the files untouched on disk if
        this build would emit an identical file.
        """
        path = Path(str(directory))
        for p in path.glob(glob):
            self.files_to_delete.add(p)

    def write(self):
        """Sync all files of this Vfs to the real filesystem.

        This performs the following actions:

        1. For each file, call disk sync to:

           1. Read the file's current contents
           2. Abort write if the data inside would not change

        2. Delete any unwritten files which were scheduled
        """
        file_paths = [file.path for file in self.files.values()]
        for file in self.files.values():
            file._write_to_disk()
        for path in self.files_to_delete:
            if not str(path) in file_paths:
                print(f"Deleting {path}")
                os.remove(path)

    def exists(self, path: str | Path):
        return str(path) in self.files

    def open(self, path: str | Path, mode: str) -> F:
        path = str(path)
        modes = set(mode)
        if "b" in modes:
            raise Exception("Binary mode not supported")
        if "r" in modes:
            raise Exception("Reading from VFS not supported.")
        if "a" in modes and path in self.files:
            return self.files[path]
        self.files[path] = file = self.file_type(path)
        return file

    # This is less nasty than dynamically generating a subclass
    # which then attaches instances to a specific Vfs on creation
    # and assigns itself as the .open value for that Vfs
    @contextmanager
    def open_ctx(self, path: str | Path, mode: str) -> Generator["VirtualFile", None, None]:
        yield self.open(path, mode)


