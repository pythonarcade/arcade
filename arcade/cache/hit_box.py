"""
A simple cache for hit boxes calculated from texture.
Hit box calculations are normally done at load time
by inspecting the contents of a loaded image.

Depending on the hit box algorithm a hit box is calculated:
* None     : Simply a box around the whole texture. No caching needed.
* Simple   : Scanning the corners for the texture
* Detailed : fairly detailed hit box generated by pymunk with detail parameter
"""

from __future__ import annotations

import gzip
import json
from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from arcade.resources import resolve
from arcade.types import Point2List

if TYPE_CHECKING:
    from arcade import Texture


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
        self._entries: OrderedDict[str, Point2List] = OrderedDict()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def get(self, name_or_texture: Union[str, "Texture"]) -> Optional[Point2List]:
        """
        Get the hit box points for a texture with a given hash
        and hit box algorithm.

        Example::

            # Get cached hit box for texture
            points = cache.get(texture)
            # Get a cache entry by string
            points = cache.get("hash|(0, 1, 2, 3)|simple|")

        :param keys: List of keys to use for the cache entry
        :param hit_box_algorithm: The hit box algorithm used
        """
        from arcade import Texture

        if isinstance(name_or_texture, Texture):
            return self._entries.get(name_or_texture.cache_name, None)
        elif isinstance(name_or_texture, str):
            return self._entries.get(name_or_texture, None)
        else:
            raise TypeError(f"Expected str or Texture: {name_or_texture}")

    def put(self, name_or_texture: Union[str, "Texture"], points: Point2List) -> None:
        """
        Store hit box points for a texture.

        Example::

            # Cache hit box for texture
            cache.put(texture, points)
            # Cache with custom string
            cache.put("my_custom_points", points)

        :param keys: List of keys to use for the cache entry
        :param points: The hit box points
        """
        from arcade import Texture

        # Points can be empty OR have at least 3 points
        if len(points) < 3 and len(points) != 0:
            raise ValueError(f"Hit box must have at least 3 points: {points}")

        if isinstance(name_or_texture, Texture):
            self._entries[name_or_texture.cache_name] = tuple(points)
        elif isinstance(name_or_texture, str):
            self._entries[name_or_texture] = tuple(points)
        else:
            raise TypeError(f"Expected str or Texture: {name_or_texture}")

    def load(self, path: Union[str, Path]) -> None:
        """
        Load a json file containing hit boxes.

        This adds the loaded hit boxes to the cache overwriting any existing
        entries and can therefore be called multiple times to populate it.

        if the file extension is ".gz" the file will be compressed.
        """
        path = resolve(path)
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

        :param path: The path to save the cache to
        :param indent: The indentation level for the json file
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

    def flush(self) -> None:
        """
        Clear the cache.
        """
        self._entries.clear()

    def __repr__(self) -> str:
        return f"HitBoxCache(entries={len(self)})"
