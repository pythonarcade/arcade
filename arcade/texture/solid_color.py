from .texture import Texture


class SolidColorTexture(Texture):
    """
    Used internally in Arcade to make colored textures.
    This is not indented to be used by the end user.

    This texture variant is mainly here it override the
    width and height property to fake texture size for
    sprites. The internal texture is always a fixed sized
    white texture that is colored by the sprite's color property.

    :param str name: Name of the texture
    :param int width: Width of the texture
    :param int height: Height of the texture
    :param img: The pillow image
    :param hit_box_points: The hit box points
    """

    def __init__(self, name, width, height, image):
        # We hardcode hit box points based on the fake width and height
        hit_box_points = (
            (-width / 2, -height / 2),
            (width / 2, -height / 2),
            (width / 2, height / 2),
            (-width / 2, height / 2)
        )
        super().__init__(
            image=image,
            hit_box_algorithm=None,
            hit_box_points=hit_box_points,
            name=name,
        )
        # Override the width and height
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
