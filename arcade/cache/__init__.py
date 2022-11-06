from typing import List, Tuple

# Texture name
# ------------
# name, xy, size, hit_box_algorithm, hit_box_detail, vertex_order
# 
# Image name
# ----------
# name, xy, size, (transform if we change pixel data in the future?)
# 
# Hit Box name
# ------------
# name, xy, size, hit_box_algorithm, vertex_order


class TextureCacheEntry:
    """
    Helper class for handling texture cache entries.
    """

    def __init__(
        self,
        *,
        name: str,
        xy: Tuple[int, int],
        size: Tuple[int, int],
        hit_box_algorithm: str,
        hit_box_detail: float,
        vertex_order: Tuple[int, int, int, int],
    ):
        self._name = name
        self._xy = xy
        self._size = size
        self._hit_box_algorithm = hit_box_algorithm
        self._hit_box_detail = hit_box_detail
        self._vertex_order = vertex_order

    @property
    def name(self) -> str:
        return self._name

    @property
    def xy(self) -> Tuple[int, int]:
        return self._xy

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @property
    def hit_box_algorithm(self) -> str:
        return self._hit_box_algorithm

    @property
    def hit_box_detail(self) -> float:
        return self._hit_box_detail

    @property
    def vertex_order(self) -> Tuple[int, int, int, int]:
        return self._vertex_order

    @classmethod
    def from_str(cls, string: str) -> "TextureCacheEntry":
        """
        Create a TextureCacheEntry from a string.

        :param string: String to parse.

        :return: TextureCacheEntry
        """
        values = parse_cache_name(string)
        name = values[0]
        xy = int(values[1]), int(values[2])
        size = int(values[3]), int(values[4])
        hit_box_algorithm = values[5]
        hit_box_detail = float(values[6])
        vertex_order = int(values[7]), int(values[8]), int(values[9]), int(values[10])
        return cls(
            name=name,
            xy=xy,
            size=size,
            hit_box_algorithm=hit_box_algorithm,
            hit_box_detail=hit_box_detail,
            vertex_order=vertex_order,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextureCacheEntry):
            return False
        return all((
            self._name == other._name,
            self._xy == other._xy,
            self._size == other._size,
            self._hit_box_algorithm == other._hit_box_algorithm,
            self._hit_box_detail == other._hit_box_detail,
            self._vertex_order == other._vertex_order,
        ))

    def __str__(self) -> str:
        return build_texture_cache_name(
            self._name,
            self._xy,
            self._size,
            self._hit_box_algorithm,
            self._hit_box_detail,
            self._vertex_order,
        )

    def __repr__(self) -> str:
        return (
            f"TextureCacheEntry("
            f"name={self._name}, "
            f"xy={self._xy}, "
            f"size={self._size}, "
            f"hit_box_algorithm={self._hit_box_algorithm}, "
            f"hit_box_detail={self._hit_box_detail}, "
            f"vertex_order={self._vertex_order}"
            f")"
        )


def build_cache_name(name, *args, separator: str = "|") -> str:
    """
    Generate a generic cache names from the given parameters

    :param str name: Name of the texture
    :param args: optional parameters
    :param separator: separator character or string between params

    :return: Formatted cache string representing passed parameters
    """
    values = [str(name)] + [str(arg) for arg in args]
    return separator.join([v for v in values])


def parse_cache_name(value: str, separator: str = "|") -> List[str]:
    """
    Parse a cache name into a list of values.

    :param str value: Cache name to parse
    :param str separator: Separator character or string between params

    :return: List of values
    """
    return value.split(separator)


def build_texture_cache_name(
    name: str,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    hit_box_algorithm: str,
    hit_box_detail: float,
    vertex_order: Tuple[int, int, int, int],
) -> str:
    """
    Generate a cache name for a texture.

    This is used to standardize the cache name for a texture
    internally in arcade.

    :param str name: Name of the texture
    :param xy: X, Y position of the texture
    :param size: Width, Height of the texture
    :param str hit_box_algorithm: Hit box algorithm
    :param float hit_box_detail: Hit box detail
    :param vertex_order: Vertex order

    :return: Formatted cache string representing passed parameters
    """
    return build_cache_name(
        name,
        xy[0], xy[0],
        size[0], size[1],
        hit_box_algorithm,
        hit_box_detail,
        vertex_order[0], vertex_order[1], vertex_order[2], vertex_order[3],
        separator="|",
    )


def build_image_cache_name(
    name: str,
    xy: Tuple[int, int],
    size: Tuple[int, int],
) -> str:
    """
    Generate a cache name for an image.

    This is used to standardize the cache name for an image
    internally in arcade.

    :param str name: Name of the texture
    :param xy: X, Y position of the texture
    :param size: Width, Height of the texture
    :param str transform: Transform applied to the image

    :return: Formatted cache string representing passed parameters
    """
    return build_cache_name(
        name,
        xy[0], xy[1],
        size[0], size[1],
        separator="|",
    )


def build_hit_box_cache_name(
    name: str,
    xy: Tuple[int, int],
    size: Tuple[int, int],
    hit_box_algorithm: str,
    hit_box_detail: int,
    vertex_order: Tuple[int, int, int, int],
) -> str:
    """
    Generate a cache name for a hit box

    :param str name: Name of the texture
    :param xy: X, Y position of the texture
    :param size: Width, Height of the texture
    :param str hit_box_algorithm: Hit box algorithm
    :param float hit_box_detail: Hit box detail
    :param vertex_order: Vertex order

    :return: Formatted cache string representing passed parameters
    """
    return build_cache_name(
        name,
        xy[0], xy[1],
        size[0], size[1],
        hit_box_algorithm,
        vertex_order[0], vertex_order[1], vertex_order[2], vertex_order[3],
        separator="|",
    )
