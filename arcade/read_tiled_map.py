import xml.etree.ElementTree as etree
import base64
import zlib

from arcade.isometric import isometric_grid_to_screen


class TiledMap:

    def __init__(self):
        self.global_tile_set = {}
        self.layers_int_data = {}
        self.layers = {}
        self.version = None
        self.orientation = None
        self.renderorder = None
        self.width = None
        self.height = None
        self.tilewidth = None
        self.tileheight = None
        self.backgroundcolor = None
        self.nextobjectid = None


class Tile:

    def __init__(self):
        self.local_id = 0
        self.width = 0
        self.height = 0
        self.source = None


class GridLocation:
    def __init__(self):
        self.tile = None
        self.center_x = 0
        self.center_y = 0


def read_tiled_map(filename: str) -> TiledMap:

    # Create a map to store this stuff in
    my_map = TiledMap()

    # Read in and parse the file
    tree = etree.parse(filename)

    # Root node should be 'map'
    map_tag = tree.getroot()
    my_map.version = map_tag.attrib["version"]
    my_map.orientation = map_tag.attrib["orientation"]
    my_map.renderorder = map_tag.attrib["renderorder"]
    my_map.width = int(map_tag.attrib["width"])
    my_map.height = int(map_tag.attrib["height"])
    my_map.tilewidth = int(map_tag.attrib["tilewidth"])
    my_map.tileheight = int(map_tag.attrib["tileheight"])
    if "backgroundcolor" in map_tag.attrib:
        backgroundcolor_string = map_tag.attrib["backgroundcolor"]
        red_hex = "0x" + backgroundcolor_string[1:3]
        green_hex = "0x" + backgroundcolor_string[3:5]
        blue_hex = "0x" + backgroundcolor_string[5:7]
        red = int(red_hex, 16)
        green = int(green_hex, 16)
        blue = int(blue_hex, 16)
        my_map.backgroundcolor = (red, green, blue)
    my_map.nextobjectid = map_tag.attrib["nextobjectid"]

    # Grab all the tilesets
    tileset_tag_list = map_tag.findall('./tileset')

    # --- Tileset Data ---

    # Loop through each tileset
    for tileset_tag in tileset_tag_list:
        firstgid = int(tileset_tag.attrib["firstgid"])

        # Grab each tile
        tile_tag_list = tileset_tag.findall("tile")

        # Loop through each tile
        for tile_tag in tile_tag_list:

            # Make a tile object
            my_tile = Tile()
            image = tile_tag.find("image")
            my_tile.local_id = tile_tag.attrib["id"]
            my_tile.width = int(image.attrib["width"])
            my_tile.height = int(image.attrib["height"])
            my_tile.source = image.attrib["source"]
            key = str(firstgid)
            my_map.global_tile_set[key] = my_tile
            firstgid += 1

    # --- Map Data ---

    # Grab each layer
    layer_tag_list = map_tag.findall('./layer')
    for layer_tag in layer_tag_list:
        layer_width = int(layer_tag.attrib['width'])
        layer_grid_ints = [[]]

        # Unzip and unencode each layer
        data = layer_tag.find("data")
        data_text = data.text.strip()
        unencoded_data = base64.b64decode(data_text)
        unzipped_data = zlib.decompress(unencoded_data)

        # Turn bytes into 4-byte integers
        byte_count = 0
        int_count = 0
        int_value = 0
        row_count = 0
        for byte in unzipped_data:
            int_value += byte << (byte_count * 8)
            byte_count += 1
            if byte_count % 4 == 0:
                byte_count = 0
                int_count += 1
                layer_grid_ints[row_count].append(int_value)
                int_value = 0
                if int_count % layer_width == 0:
                    row_count += 1
                    layer_grid_ints.append([])
        layer_grid_ints.pop()
        my_map.layers_int_data[layer_tag.attrib["name"]] = layer_grid_ints

        layer_grid_objs = []
        for row_index, row in enumerate(layer_grid_ints):
            layer_grid_objs.append([])
            for column_index, column in enumerate(row):
                grid_location = GridLocation()
                if layer_grid_ints[row_index][column_index] != 0:
                    key = str(layer_grid_ints[row_index][column_index])
                    grid_location.tile = my_map.global_tile_set[key]

                    if my_map.renderorder == "right-down":
                        adjusted_row_index = my_map.height - row_index - 1
                    else:
                        adjusted_row_index = row_index

                    if my_map.orientation == "orthogonal":
                        grid_location.center_x = column_index * my_map.tilewidth + my_map.tilewidth // 2
                        grid_location.center_y = adjusted_row_index * my_map.tileheight + my_map.tilewidth // 2
                    else:
                        grid_location.center_x,  grid_location.center_y = isometric_grid_to_screen(column_index, row_index, my_map.width, my_map.height, my_map.tilewidth, my_map.tileheight)


                layer_grid_objs[row_index].append(grid_location)

        my_map.layers[layer_tag.attrib["name"]] = layer_grid_objs

    return my_map
