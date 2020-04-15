"""
Functions and classes for managing a map saved in the .tmx format.

Typically these .tmx maps are created using the `Tiled Map Editor`_.

For more information, see the `Platformer Tutorial`_.

.. _Tiled Map Editor: https://www.mapeditor.org/
.. _Platformer Tutorial: http://arcade.academy/examples/platform_tutorial/index.html


"""

from typing import Optional, List, cast
import math
import copy
import pytiled_parser
import os
from pathlib import Path

from arcade import Sprite
from arcade import AnimatedTimeBasedSprite
from arcade import AnimationKeyframe
from arcade import SpriteList
from arcade import load_texture
from arcade import Texture
from arcade.arcade_types import Point

_FLIPPED_HORIZONTALLY_FLAG = 0x80000000
_FLIPPED_VERTICALLY_FLAG = 0x40000000
_FLIPPED_DIAGONALLY_FLAG = 0x20000000


def read_tmx(tmx_file: str) -> pytiled_parser.objects.TileMap:
    """
    Given a .tmx, this will read in a tiled map, and return
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

    # If we should pull from local resources, replace with proper path
    if isinstance(tmx_file, str) and str(tmx_file).startswith(":resources:"):
        import os
        path = os.path.dirname(os.path.abspath(__file__))
        tmx_file = f"{path}/resources/{tmx_file[11:]}"

    tile_map = pytiled_parser.parse_tile_map(tmx_file)

    return tile_map


def get_tilemap_layer(map_object: pytiled_parser.objects.TileMap,
                      layer_name: str) -> Optional[pytiled_parser.objects.Layer]:
    """
    Given a TileMap and a layer name, this returns the TileLayer.

    :param pytiled_parser.objects.TileMap map_object: The map read in by the read_tmx function.
    :param str layer_name: A string to match the layer name. Case sensitive.

    :returns: A TileLayer, or None if no layer was found.

    """

    assert isinstance(map_object, pytiled_parser.objects.TileMap)
    assert isinstance(layer_name, str)

    for layer in map_object.layers:
        if layer.name == layer_name:
            return layer

    return None


def _get_tile_by_gid(map_object: pytiled_parser.objects.TileMap,
                     tile_gid: int) -> Optional[pytiled_parser.objects.Tile]:

    flipped_diagonally = False
    flipped_horizontally = False
    flipped_vertically = False

    if tile_gid & _FLIPPED_HORIZONTALLY_FLAG:
        flipped_horizontally = True
        tile_gid -= _FLIPPED_HORIZONTALLY_FLAG

    if tile_gid & _FLIPPED_DIAGONALLY_FLAG:
        flipped_diagonally = True
        tile_gid -= _FLIPPED_DIAGONALLY_FLAG

    if tile_gid & _FLIPPED_VERTICALLY_FLAG:
        flipped_vertically = True
        tile_gid -= _FLIPPED_VERTICALLY_FLAG

    for tileset_key, tileset in map_object.tile_sets.items():

        if tile_gid < tileset_key:
            continue

        tile_ref = tileset.tiles.get(tile_gid - tileset_key)

        # No specific tile info, but there is a tile sheet
        if tile_ref is None \
                and tileset.image is not None \
                and tileset_key <= tile_gid < tileset_key + tileset.tile_count:
            image = pytiled_parser.objects.Image(source=tileset.image.source)
            tile_ref = pytiled_parser.objects.Tile(id_=(tile_gid - tileset_key),
                                                   image=image)

        if tile_ref is None:
            continue
        my_tile = copy.copy(tile_ref)
        my_tile.tileset = tileset
        my_tile.flipped_vertically = flipped_vertically
        my_tile.flipped_diagonally = flipped_diagonally
        my_tile.flipped_horizontally = flipped_horizontally
        return my_tile
    return None


def _get_tile_by_id(map_object: pytiled_parser.objects.TileMap,
                    tileset: pytiled_parser.objects.TileSet,
                    tile_id: int) -> Optional[pytiled_parser.objects.Tile]:
    for tileset_key, cur_tileset in map_object.tile_sets.items():
        if cur_tileset is tileset:
            for tile_key, tile in cur_tileset.tiles.items():
                if tile_id == tile.id_:
                    return tile
    return None

def _get_image_info_from_tileset(tile):
    image_x = 0
    image_y = 0
    if tile.tileset.image is not None:
        row = tile.id_ // tile.tileset.columns
        image_y = row * tile.tileset.max_tile_size.height
        col = tile.id_ % tile.tileset.columns
        image_x = col * tile.tileset.max_tile_size.width

    if tile.image and tile.image.size:
        # Individual image, use image width and height
        width = tile.image.size.width
        height = tile.image.size.height
    else:
        # Sprite sheet, use max width/height from sheet
        width = tile.tileset.max_tile_size.width
        height = tile.tileset.max_tile_size.height

    return image_x, image_y, width, height

def _get_image_source(tile: pytiled_parser.objects.Tile,
                      base_directory: Optional[str],
                      map_directory: Optional[str]):
    image_file = None
    if tile.image:
        image_file = tile.image.source
    elif tile.tileset.image:
        image_file = tile.tileset.image.source

    if not image_file:
        print(f"Warning for tile {tile.id_}, no image source listed either for individual tile, or as a tileset.")
        return None

    if os.path.exists(image_file):
        return image_file

    if base_directory:
        try2 = Path(base_directory, image_file)
        if os.path.exists(try2):
            return try2

    if map_directory:
        try3 = Path(map_directory, image_file)
        if os.path.exists(try3):
            return try3

    print(f"Warning, can't file image {image_file} for tile {tile.id_} - {base_directory}")
    return None


def _create_sprite_from_tile(map_object: pytiled_parser.objects.TileMap,
                             tile: pytiled_parser.objects.Tile,
                             scaling: float = 1.0,
                             base_directory: str = None):
    """
    Given a tile from the parser, see if we can create a sprite from it
    """

    # --- Step 1, find a reference to an image this is going to be based off of
    map_source = map_object.tmx_file
    map_directory = os.path.dirname(map_source)
    image_file = _get_image_source(tile, base_directory, map_directory)

    # print(f"Creating tile: {tmx_file}")
    if tile.animation:
        # my_sprite = AnimatedTimeSprite(tmx_file, scaling)
        my_sprite: Sprite = AnimatedTimeBasedSprite(image_file, scaling)
    else:
        image_x, image_y, width, height = _get_image_info_from_tileset(tile)

        my_sprite = Sprite(image_file,
                           scaling,
                           image_x,
                           image_y,
                           width,
                           height)

    if tile.properties is not None and len(tile.properties) > 0:
        for my_property in tile.properties:
            my_sprite.properties[my_property.name] = my_property.value

        # print(tile.image.source, my_sprite.center_x, my_sprite.center_y)
    if tile.objectgroup is not None:

        if len(tile.objectgroup) > 1:
            print(f"Warning, only one hit box supported for tile with image {tile.image.source}.")

        for hitbox in tile.objectgroup:
            points: List[Point] = []
            if isinstance(hitbox, pytiled_parser.objects.RectangleObject):
                if hitbox.size is None:
                    print(f"Warning: Rectangle hitbox created for without a "
                          f"height or width for {tile.image.source}. Ignoring.")
                    continue

                # print(my_sprite.width, my_sprite.height)
                sx = hitbox.location[0] - (my_sprite.width / (scaling * 2))
                sy = -(hitbox.location[1] - (my_sprite.height / (scaling * 2)))
                ex = (hitbox.location[0] + hitbox.size[0]) - (my_sprite.width / (scaling * 2))
                ey = -((hitbox.location[1] + hitbox.size[1]) - (my_sprite.height / (scaling * 2)))

                # print(f"Size: {hitbox.size} Location: {hitbox.location}")
                p1 = [sx, sy]
                p2 = [ex, sy]
                p3 = [ex, ey]
                p4 = [sx, ey]
                # print(f"w:{my_sprite.width:.1f}, h:{my_sprite.height:.1f}", end=", ")
                points = [p1, p2, p3, p4]
                # for point in points:
                #     print(f"({point[0]:.1f}, {point[1]:.1f}) ")
                # print()

            elif isinstance(hitbox, pytiled_parser.objects.PolygonObject) \
                    or isinstance(hitbox, pytiled_parser.objects.PolylineObject):
                for point in hitbox.points:
                    adj_x = point[0] + hitbox.location[0] - my_sprite.width / (scaling * 2)
                    adj_y = -(point[1] + hitbox.location[1] - my_sprite.height / (scaling * 2))
                    adj_point = [adj_x, adj_y]
                    points.append(adj_point)

                # If we have a polyline, and it is closed, we need to
                # remove the duplicate end-point
                if points[0][0] == points[-1][0] and points[0][1] == points[-1][1]:
                    points.pop()

            elif isinstance(hitbox, pytiled_parser.objects.ElipseObject):
                if hitbox.size is None:
                    print(f"Warning: Ellipse hitbox created for without a height "
                          f"or width for {tile.image.source}. Ignoring.")
                    continue

                # print(f"Size: {hitbox.size} Location: {hitbox.location}")

                hw = hitbox.size[0] / 2
                hh = hitbox.size[1] / 2
                cx = hitbox.location[0] + hw
                cy = hitbox.location[1] + hh

                acx = cx - (my_sprite.width / (scaling * 2))
                acy = cy - (my_sprite.height / (scaling * 2))

                # print(f"acx: {acx} acy: {acy} cx: {cx} cy: {cy} hh: {hh} hw: {hw}")

                total_steps = 8
                angles = [step / total_steps * 2 * math.pi for step in range(total_steps)]
                for angle in angles:
                    x = (hw * math.cos(angle) + acx)
                    y = (-(hh * math.sin(angle) + acy))
                    point = [x, y]
                    points.append(point)

                # for point in points:
                #     print(f"({point[0]:.1f}, {point[1]:.1f}) ")
                # print()

            else:
                print(f"Warning: Hitbox type {type(hitbox)} not supported.")

            my_sprite.points = points

    if tile.animation is not None:
        # Animated image
        key_frame_list = []
        # Loop through each frame
        for frame in tile.animation:
            # Get the tile for the frame
            frame_tile = _get_tile_by_id(map_object, tile.tileset, frame.tile_id)
            if frame_tile:

                image_file = _get_image_source(frame_tile, base_directory, map_directory)

                # Does the tile have an image?
                if frame_tile.image:
                    # Yes, use it
                    texture = load_texture(image_file)
                else:
                    # No image for tile? Pull from tilesheet
                    image_x, image_y, width, height = _get_image_info_from_tileset(frame_tile)

                    texture = load_texture(image_file,
                                           image_x, image_y,
                                           width, height)

                key_frame = AnimationKeyframe(frame.tile_id, frame.duration, texture)
                key_frame_list.append(key_frame)
                # If this is the first texture in the animation, go ahead and
                # set it as the current texture.
                if len(key_frame_list) == 1:
                    my_sprite.texture = key_frame.texture
                # print(f"Add tile {frame.tile_id} for keyframe. Source: {frame_tile.image.source}")

        cast(AnimatedTimeBasedSprite, my_sprite).frames = key_frame_list

    return my_sprite


def _process_object_layer(map_object: pytiled_parser.objects.TileMap,
                          layer: pytiled_parser.objects.ObjectLayer,
                          scaling: float = 1,
                          base_directory: str = "") -> SpriteList:
    sprite_list: SpriteList = SpriteList()

    for cur_object in layer.tiled_objects:
        if cur_object.gid is None:
            print("Warning: Currently only tiles (not objects) are supported in object layers.")
            continue

        tile = _get_tile_by_gid(map_object, cur_object.gid)
        my_sprite = _create_sprite_from_tile(map_object, tile, scaling=scaling,
                                             base_directory=base_directory)

        x = cur_object.location.x * scaling
        y = (map_object.map_size.height * map_object.tile_size[1] - cur_object.location.y) * scaling

        my_sprite.width = width = cur_object.size[0] * scaling
        my_sprite.height = height = cur_object.size[1] * scaling
        centerX = width / 2
        centerY = height / 2
        rotation = -math.radians(cur_object.rotation)
        cosRotation = math.cos(rotation)
        sinRotation = math.sin(rotation)
        rotatedCenterX = centerX * cosRotation - centerY * sinRotation
        rotatedCenterY = centerX * sinRotation + centerY * cosRotation

        my_sprite.position = (x + rotatedCenterX, y + rotatedCenterY)
        my_sprite.angle = math.degrees(rotation)

        if cur_object.properties is not None and 'change_x' in cur_object.properties:
            my_sprite.change_x = float(cur_object.properties['change_x'])

        if cur_object.properties is not None and 'change_y' in cur_object.properties:
            my_sprite.change_y = float(cur_object.properties['change_y'])

        if cur_object.properties is not None and 'boundary_bottom' in cur_object.properties:
            my_sprite.boundary_bottom = float(cur_object.properties['boundary_bottom'])

        if cur_object.properties is not None and 'boundary_top' in cur_object.properties:
            my_sprite.boundary_top = float(cur_object.properties['boundary_top'])

        if cur_object.properties is not None and 'boundary_left' in cur_object.properties:
            my_sprite.boundary_left = float(cur_object.properties['boundary_left'])

        if cur_object.properties is not None and 'boundary_right' in cur_object.properties:
            my_sprite.boundary_right = float(cur_object.properties['boundary_right'])

        if cur_object.properties is not None:
            my_sprite.properties.update(cur_object.properties)
        # sprite.properties
        sprite_list.append(my_sprite)
    return sprite_list


def _process_tile_layer(map_object: pytiled_parser.objects.TileMap,
                        layer: pytiled_parser.objects.TileLayer,
                        scaling: float = 1,
                        base_directory: str = "") -> SpriteList:
    sprite_list: SpriteList = SpriteList()
    map_array = layer.data

    # Loop through the layer and add in the wall list
    for row_index, row in enumerate(map_array):
        for column_index, item in enumerate(row):
            # Check for empty square
            if item == 0:
                continue

            tile = _get_tile_by_gid(map_object, item)
            if tile is None:
                print(f"Warning, couldn't find tile for item {item} in layer "
                      f"'{layer.name}' in file '{map_object.tmx_file}'.")
                continue

            my_sprite = _create_sprite_from_tile(map_object, tile, scaling=scaling,
                                                 base_directory=base_directory)

            if my_sprite is None:
                print(f"Warning: Could not create sprite number {item} in layer '{layer.name}' {tile.image.source}")
            else:
                my_sprite.center_x = column_index * (map_object.tile_size[0] * scaling) + my_sprite.width / 2
                my_sprite.center_y = (map_object.map_size.height - row_index - 1) \
                    * (map_object.tile_size[1] * scaling) + my_sprite.height / 2

                sprite_list.append(my_sprite)

    return sprite_list


def process_layer(map_object: pytiled_parser.objects.TileMap,
                  layer_name: str,
                  scaling: float = 1,
                  base_directory: str = "") -> SpriteList:
    """
    This takes a map layer returned by the read_tmx function, and creates Sprites for it.

    :param map_object: The TileMap read in by read_tmx.
    :param layer_name: The name of the layer that we are creating sprites for.
    :param scaling: Scaling the layer up or down.
                    (Note, any number besides 1 can create a tearing effect,
                    if numbers don't evenly divide.)
    :param base_directory: Base directory of the file, that we start from to
                           load images.
    :returns: A SpriteList.

    """

    if len(base_directory) > 0 and not base_directory.endswith("/"):
        base_directory += "/"

    layer = get_tilemap_layer(map_object, layer_name)
    if layer is None:
        print(f"Warning, no layer named '{layer_name}'.")
        return SpriteList()

    if isinstance(layer, pytiled_parser.objects.TileLayer):
        return _process_tile_layer(map_object, layer, scaling, base_directory)

    elif isinstance(layer, pytiled_parser.objects.ObjectLayer):
        return _process_object_layer(map_object, layer, scaling, base_directory)

    print(f"Warning, layer '{layer_name}' has unexpected type. '{type(layer)}'")
    return SpriteList()
