"""
Functions and classes for managing a map created in the "Tiled Map Editor"
"""

from arcade import Sprite
from arcade import SpriteList
import math
import pytiled_parser


def read_tmx(tmx_file: str) -> pytiled_parser.objects.TileMap:
    """
    Given a tmx_file, this will read in a tiled map, and return
    a TiledMap object.

    Given a tsx_file, the map will use it as the tileset.
    If tsx_file is not specified, it will use the tileset specified
    within the tmx_file.

    Important: Tiles must be a "collection" of images.

    Hitboxes can be drawn around tiles in the tileset editor,
    but only polygons are supported.
    (This is a great area for PR's to improve things.)

    :param str tmx_file: String with name of our TMX file

    :returns: Map
    :rtype: TiledMap
    """

    tile_map = pytiled_parser.parse_tile_map(tmx_file)
    if tile_map.background_color:
        color = pytiled_parser.utilities.parse_color(tile_map.background_color)
        tile_map.background_color = (color.red, color.green, color.blue)

    return tile_map


def get_tilemap_layer(map_object: pytiled_parser.objects.TileMap,
                      layer_name: str):

    assert isinstance(map_object, pytiled_parser.objects.TileMap)
    assert isinstance(layer_name, str)

    for layer in map_object.layers:
        if layer.name == layer_name:
            return layer

    return None


def get_tile(map_object: pytiled_parser.objects.TileMap, gid: int) -> pytiled_parser.objects.Tile:
    for tileset_key, tileset in map_object.tile_sets.items():
        for tile_key, tile in tileset.tiles.items():
            tile_gid = tile.id + tileset_key
            if tile_gid == gid:
                return tile
    return None


def generate_sprites_from_layer(map_object: pytiled_parser.objects.TileMap,
                                layer_name: str,
                                scaling: float = 1,
                                base_directory: str = "") -> SpriteList:

    if len(base_directory) > 0 and not base_directory.endswith("/"):
        base_directory += "/"
    sprite_list = SpriteList()

    layer = get_tilemap_layer(map_object, layer_name)
    if layer is None:
        print(f"Warning, no layer named '{layer_name}'.")
        return sprite_list

    map_array = layer.data

    # Loop through the layer and add in the wall list
    for row_index, row in enumerate(map_array):
        for column_index, item in enumerate(row):
            # Check for empty square
            if item == 0:
                continue

            tile = get_tile(map_object, item)
            if tile is None:
                print(f"Warning, couldn't find tile for {item}")
                continue

            tmx_file = base_directory + tile.image.source

            my_sprite = Sprite(tmx_file, scaling)
            my_sprite.right = column_index * (map_object.tile_size[0] * scaling)
            my_sprite.top = (map_object.map_size.height - row_index - 1) * (map_object.tile_size[1] * scaling)


            if tile.properties is not None and len(tile.properties) > 0:
                for property in tile.properties:
                    my_sprite.properties[property.name] = property.value

            # print(tile.image.source, my_sprite.center_x, my_sprite.center_y)
            if tile.hitboxes is not None and len(tile.hitboxes) > 0:
                if len(tile.hitboxes) > 1:
                    print(f"Warning, only one hit box supported for tile with image {tile.image.source}.")
                for hitbox in tile.hitboxes:

                    if hitbox.hitbox_type == "Rectangle":
                        p1 = hitbox.x, hitbox.y
                        p2 = hitbox.x + hitbox.width, hitbox.y
                        p3 = hitbox.x + hitbox.width, hitbox.y + hitbox.height
                        p4 = hitbox.x, hitbox.y + hitbox.height
                        my_sprite.points = p1, p2, p3, p4

                    elif hitbox.hitbox_type == "Polygon":
                        points = []
                        for point in hitbox.points:
                            adj_x = point[0] + hitbox.x
                            adj_y = point[1] + hitbox.y
                            adj_point = [adj_x, adj_y]
                            points.append(adj_point)
                        my_sprite.points = points

                    elif hitbox.hitbox_type == "Polyline":
                        points = []
                        for point in hitbox.points:
                            adj_x = point[0] + hitbox.x
                            adj_y = point[1] + hitbox.y
                            adj_point = [adj_x, adj_y]
                            points.append(adj_point)

                        # See if we need to close the polyline
                        if points[0][0] != points[-1][0] or points[0][1] != points[-1][1]:
                            points.append(points[0])

                        my_sprite.points = points

                    elif hitbox.hitbox_type == "Ellipse":
                        w = hitbox.width
                        h = hitbox.height
                        cx = hitbox.x + w / 2
                        cy = hitbox.y + h / 2
                        total_steps = 8
                        points = []
                        angles = [step / total_steps * 2 * math.pi for step in range(total_steps)]
                        for angle in angles:
                            x = w * math.cos(angle) + cx
                            y = h * math.sin(angle) + cy
                            point = x, y
                            points.append(point)

                        my_sprite.points = points

                    else:
                        print(f"Warning: Hitbox type {hitbox.hitbox_type} not supported.")

            sprite_list.append(my_sprite)

    return sprite_list
