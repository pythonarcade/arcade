from arcade.shape_list import ShapeElementList, create_line
from arcade.types import RGBA255


def isometric_grid_to_screen(
    tile_x: int, tile_y: int, width: int, height: int, tile_width: int, tile_height: int
) -> tuple[int, int]:
    """
    Convert isometric grid coordinates to screen coordinates.

    Args:
        tile_x: The x coordinate of the tile in the isometric grid.
        tile_y: The y coordinate of the tile in the isometric grid.
        width: The width of the screen.
        height: The height of the screen.
        tile_width: The width of a tile in pixels.
        tile_height: The height of a tile in pixels.
    """
    screen_x = tile_width * tile_x // 2 + height * tile_width // 2 - tile_y * tile_width // 2
    screen_y = (
        (height - tile_y - 1) * tile_height // 2
        + width * tile_height // 2
        - tile_x * tile_height // 2
    )
    return screen_x, screen_y


def screen_to_isometric_grid(
    screen_x: int, screen_y: int, width: int, height: int, tile_width: int, tile_height: int
) -> tuple[int, int]:
    """
    Convert screen coordinates to isometric grid coordinates.

    Args:
        screen_x: The x coordinate on the screen.
        screen_y: The y coordinate on the screen.
        width: The width of the screen.
        height: The height of the screen.
        tile_width: The width of a tile in pixels.
        tile_height: The height of a tile in pixels.
    """
    x2 = (1 / tile_width * screen_x / 2 - 1 / tile_height * screen_y / 2 + width / 2) * 2 - (
        width / 2 + 0.5
    )
    y2 = (height - 1) - (
        (1 / tile_width * screen_x / 2 + 1 / tile_height * screen_y / 2) * 2 - (width / 2 + 0.5)
    )
    x2 = round(x2)
    y2 = round(y2)
    return x2, y2


def create_isometric_grid_lines(
    width: int, height: int, tile_width: int, tile_height: int, color: RGBA255, line_width: int
) -> ShapeElementList:
    """
    Create a ShapeElementList of isometric grid lines.

    Args:
        width: The width of the grid in tiles.
        height: The height of the grid in tiles.
        tile_width: The width of a tile in pixels.
        tile_height: The height of a tile in pixels.
        color: The color of the lines.
        line_width: The width of the lines.
    """
    # Grid lines 1
    shape_list: ShapeElementList = ShapeElementList()

    for tile_row in range(-1, height):
        tile_x = 0
        start_x, start_y = isometric_grid_to_screen(
            tile_x, tile_row, width, height, tile_width, tile_height
        )
        tile_x = width - 1
        end_x, end_y = isometric_grid_to_screen(
            tile_x, tile_row, width, height, tile_width, tile_height
        )

        start_x -= tile_width // 2
        end_y -= tile_height // 2

        line = create_line(start_x, start_y, end_x, end_y, color, line_width=line_width)
        shape_list.append(line)

    # Grid lines 2
    for tile_column in range(-1, width):
        tile_y = 0
        start_x, start_y = isometric_grid_to_screen(
            tile_column, tile_y, width, height, tile_width, tile_height
        )
        tile_y = height - 1
        end_x, end_y = isometric_grid_to_screen(
            tile_column, tile_y, width, height, tile_width, tile_height
        )

        start_x += tile_width // 2
        end_y -= tile_height // 2

        line = create_line(start_x, start_y, end_x, end_y, color, line_width=line_width)
        shape_list.append(line)

    return shape_list
