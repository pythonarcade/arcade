import os
from pathlib import Path
from typing import Union


class Vfs:
    """
    Virtual filesystem: write files in-memory, then sync to real fs when done.
    Used to avoid touching files that would not change.
    This avoids invalidating sphinx cache and causing endless rebuild loops w/
    sphinx-autobuild.
    """
    def __init__(self):
        self.files: dict[str, VirtualFile] = dict()
        self.files_to_delete: set[Path] = set()

    def delete_glob(self, directory: Union[str, Path], glob: str):
        """
        Glob for all files on disk that were created by the previous build.
        These files should be deleted if this build does not emit them.
        Deletion will not be attempted until this Vfs is synced to disk.

        Doing it this way allows us to leave the files untouched on disk if
        this build would emit an identical file.
        """
        path = Path(str(directory))
        for p in path.glob('*.rst'):
            self.files_to_delete.add(p)

    def write(self):
        """
        Sync all files of this Vfs to the real filesystem, and delete any files
        from previous builds.
        """
        file_paths = [file.path for file in self.files.values()]
        for file in self.files.values():
            file._write_to_disk()
        for path in self.files_to_delete:
            if not str(path) in file_paths:
                print(f"Deleting {path}")
                os.remove(path)

    def exists(self, path: Union[str, Path]):
        return str(path) in self.files

    def open(self, path: Union[str, Path], mode: str):
        path = str(path)
        modes = set(mode)
        if "b" in modes:
            raise Exception("Binary mode not supported")
        if "r" in modes:
            raise Exception("Reading from VFS not supported.")
        if "a" in modes and path in self.files:
            return self.files[path]
        self.files[path] = file = VirtualFile(path)
        return file


class VirtualFile:

    def __init__(self, path: str):
        self.path = path
        self.content = ''

    def write(self, str: str):
        self.content += str

    def close(self):
        pass

    def _write_to_disk(self):
        before = None
        try:
            with open(self.path, "r") as f:
                before = f.read()
        except:
            pass
        if before != self.content:
            print(f"Writing {self.path}")
            with open(self.path, "w") as f:
                f.write(self.content)
