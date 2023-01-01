"""
A simple cache for hit boxes calculated from texture.
Hit box calculations are normally done at load time
by inspecting the contents of a loaded image.

Depending on the hit box algorithm a hit box is calculated:
* None     : Simply a box around the whole texture. No caching needed.
* Simple   : Scanning the corners for the texture
* Detailed : fairly detailed hit box generated by pymunk with detail parameter
"""
import gzip
import json
from pathlib import Path
from typing import Any, List, Optional, Union
from collections import OrderedDict

from arcade.arcade_types import PointList
from arcade.resources import resolve_resource_path

# TODO: include version number in cache file


class HitBoxCache:
    """
    A simple cache for hit box points for textures.

    These are calculated when loading a texture
    depending on the selected hit box algorithm.

    Points are stored as a tuple of xy points since
    it's important that they are immutable.
    """
    VERSION = 1

    def __init__(self):
        self._entries: OrderedDict[str, PointList] = OrderedDict()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def get(self, keys: List[Any]) -> Optional[PointList]:
        """
        Get the hit box points for a texture with a given hash
        and hit box algorithm.

        Example::

            # Get points with key "hash-simple"
            cache.get(["hash", "simple"])

        :param keys: List of keys to use for the cache entry
        :param str hit_box_algorithm: The hit box algorithm used
        """
        key = self._gen_key(*keys)
        return self._entries.get(key, None)

    def put(self, keys: List[Any], points: PointList) -> None:
        """
        Store hit box points usually for a texture.

        Keys are joined as strings with a "-" separator.

        Example::

            # Simple hit box points
            cache.put(["hash", "simple"], points)
            # Detailed hit box points
            cache.put(["hash", "detailed", 4.5], points)

        :param List[Any] keys: List of keys to use for the cache entry
        :param PointList points: The hit box points
        """
        # Points can be empty OR have at least 3 points
        if len(points) < 3 and len(points) != 0:
            raise ValueError(f"Hit box must have at least 3 points: {points}")

        key = self._gen_key(*keys)
        self._entries[key] = tuple(points)

    def load(self, path: Union[str, Path]) -> None:
        """
        Load a json file containing hit boxes.

        This adds the loaded hit boxes to the cache overwriting any existing
        entries and can therefore be called multiple times to populate it.

        if the file extension is ".gz" the file will be compressed.
        """
        path = resolve_resource_path(path)
        if path.suffix == ".gz":
            with gzip.open(path, mode="rb") as fd:
                data = json.loads(fd.read())
        else:
            with open(path, mode="r") as fd:
                data = json.loads(fd.read())

        for key, value in data.items():
            self._entries[key] = tuple(value)

    def save(self, path: Path, indent: int = 0) -> None:
        """
        Save the hit box cache to disk.

        This can be used to pre-populate the cache to
        reduce the time it takes to load textures.

        if the file extension is ".gz" the file will be compressed.

        :param Path path: The path to save the cache to
        :param int indent: The indentation level for the json file
        """
        if indent == 0:
            data_str = json.dumps(self._entries)
        else:
            data_str = json.dumps(self._entries, indent=indent)

        data = data_str.encode("utf-8")

        if path.suffix == ".gz":
            data = gzip.compress(data)

        with open(path, mode="wb") as fd:
            fd.write(data)

    def clear(self) -> None:
        """
        Clear the cache.
        """
        self._entries.clear()

    def __repr__(self) -> str:
        return f"HitBoxCache(entries={len(self)})"

    def _gen_key(self, *args) -> str:
        """Standardized way to generate a key"""
        return "-".join(str(v).lower() for v in args)
