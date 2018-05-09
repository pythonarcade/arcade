import xml.etree.ElementTree as etree
import base64
import zlib


class TiledMap:

    def __init__(self):
        self.global_tile_set = {}
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


def read_tiled_map(filename):

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
    my_map.backgroundcolor = map_tag.attrib["backgroundcolor"]
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
        layer_grid = [[]]

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
                layer_grid[row_count].append(int_value)
                int_value = 0
                if int_count % layer_width == 0:
                    row_count += 1
                    layer_grid.append([])
        layer_grid.pop()
        my_map.layers[layer_tag.attrib["name"]] = layer_grid
        return my_map
