from PIL.Image import Image

from arcade.types import Point, Point2List

from .base import HitBoxAlgorithm


class SimpleHitBoxAlgorithm(HitBoxAlgorithm):
    """
    Simple hit box algorithm. This algorithm attempts to trim out transparent pixels
    from an image to create a hit box.
    """

    def calculate(self, image: Image, **kwargs) -> Point2List:
        """
        Given an RGBA image, this returns points that make up a hit box around it. Attempts
        to trim out transparent pixels.

        Args:
            image: Image get hit box from.
        """
        if image.mode != "RGBA":
            raise ValueError("Image mode is not RGBA. image.convert('RGBA') is needed.")

        # Convert the image into one channel alpha since we don't care about RGB values
        image = image.getchannel("A")
        bbox = image.getbbox()
        # If there is no bounding box the image is empty
        if bbox is None:
            return self.create_bounding_box(image)

        left_border, top_border, right_border, bottom_border = bbox
        right_border -= 1
        bottom_border -= 1

        def _check_corner_offset(
            start_x: int, start_y: int, x_direction: int, y_direction: int
        ) -> int:
            bad = False
            offset = 0
            while not bad:
                y = start_y + (offset * y_direction)
                x = start_x
                for _ in range(offset + 1):
                    alpha = image.getpixel((x, y))
                    # print(f"({x}, {y}) = {my_pixel} | ", end="")
                    if alpha != 0:
                        bad = True
                        break
                    y -= y_direction
                    x += x_direction
                # print(f" - {bad}")
                if not bad:
                    offset += 1
            # print(f"offset: {offset}")
            return offset

        def _r(point: tuple[float, float], height: int, width: int) -> Point:
            return point[0] - width / 2, (height - point[1]) - height / 2

        top_left_corner_offset = _check_corner_offset(left_border, top_border, 1, 1)
        top_right_corner_offset = _check_corner_offset(right_border, top_border, -1, 1)
        bottom_left_corner_offset = _check_corner_offset(left_border, bottom_border, 1, -1)
        bottom_right_corner_offset = _check_corner_offset(right_border, bottom_border, -1, -1)

        p1 = left_border + top_left_corner_offset, top_border
        p2 = (right_border + 1) - top_right_corner_offset, top_border
        p3 = (right_border + 1), top_border + top_right_corner_offset
        p4 = (right_border + 1), (bottom_border + 1) - bottom_right_corner_offset
        p5 = (right_border + 1) - bottom_right_corner_offset, (bottom_border + 1)
        p6 = left_border + bottom_left_corner_offset, (bottom_border + 1)
        p7 = left_border, (bottom_border + 1) - bottom_left_corner_offset
        p8 = left_border, top_border + top_left_corner_offset

        result = []

        h = image.height
        w = image.width

        result.append(_r(p7, h, w))
        if bottom_left_corner_offset:
            result.append(_r(p6, h, w))

        result.append(_r(p5, h, w))
        if bottom_right_corner_offset:
            result.append(_r(p4, h, w))

        result.append(_r(p3, h, w))
        if top_right_corner_offset:
            result.append(_r(p2, h, w))

        result.append(_r(p1, h, w))
        if top_left_corner_offset:
            result.append(_r(p8, h, w))

        # Remove duplicates
        return tuple(dict.fromkeys(result))  # type: ignore
