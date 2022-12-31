"""
A simple cache for hit boxes calculated from texture.
Hit box calculations are normally done at load time
by inspecting the contents of a loaded image.

Depending on the hit box algorithm a hit box is calculated:
* None     : Simply a box around the whole texture. No caching needed.
* Simple   : Scanning the corners for the texture
* Detailed : fairly detailed hit box generated by pymunk with detail parameter
"""
import json
from pathlib import Path
from typing import Dict, Optional, Union

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
        self._entries: Dict[str, PointList] = {}

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    def load(self, path: Union[str, Path]) -> None:
        """
        Load a json file containing hit boxes.

        This adds the loaded hit boxes to the cache overwriting any existing
        entries and can therefore be called multiple times to populate it.
        """
        path = resolve_resource_path(path)
        with open(path, mode="r") as fd:
            data = json.loads(fd.read())

        for key, value in data.items():
            self._entries[key] = tuple(value)

    def get(self, hash: str, hit_box_algorithm: str) -> Optional[PointList]:
        """
        Get the hit box points for a texture with a given hash
        and hit box algorithm.

        :param str hash: The hash of the texture
        :param str hit_box_algorithm: The hit box algorithm used
        """
        hit_box_algorithm = hit_box_algorithm.lower()
        return self._entries.get(f"{hash}-{hit_box_algorithm}", None)

    def put(self, hash: str, hit_box_algorithm: str, points: PointList) -> None:
        """
        Store hit box points for a texture with a given hash
        and hit box algorithm.

        :param str hash: The hash of the texture
        :param str hit_box_algorithm: The hit box algorithm used
        :param PointList points: The hit box points
        """
        # Points can be empty OR have at least 3 points
        if len(points) < 3 and len(points) != 0:
            raise ValueError(f"Hit box must have at least 3 points: {points}")

        hit_box_algorithm = hit_box_algorithm.lower()
        self._entries[f"{hash}-{hit_box_algorithm}"] = tuple(points)

    def save(self, path: Union[str, Path], indent: int = 0) -> None:
        """
        Save the hit box cache to disk.

        This can be used to pre-populate the cache to
        reduce the time it takes to load textures.

        :param Path path: The path to save the cache to
        :param int indent: The indentation level for the json file
        """
        with open(path, mode="w") as fd:
            if indent == 0:
                fd.write(json.dumps(self._entries))
            else:
                fd.write(json.dumps(self._entries, indent=indent))

    def clear(self) -> None:
        """
        Clear the cache.
        """
        self._entries.clear()

    def __repr__(self) -> str:
        return f"HitBoxCache(entries={len(self)})"
