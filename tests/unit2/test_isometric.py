# """
# Example of displaying an isometric map.
#
# Isometric map created with Tiled Map Editor: https://www.mapeditor.org/
# Tiles by Kenney: http://kenney.nl/assets/isometric-dungeon-tiles
# """
#
# import arcade
# import os
#
# from pathlib import Path
#
# SPRITE_SCALING = 0.5
#
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
#
# # How many pixels to keep as a minimum margin between the character
# # and the edge of the screen.
# VIEWPORT_MARGIN = 200
#
# MOVEMENT_SPEED = 5
#
#
# def read_sprite_list(grid, sprite_list):
#     for row in grid:
#         for grid_location in row:
#             if grid_location.tile is not None:
#                 tile_sprite = arcade.Sprite(grid_location.tile.source, SPRITE_SCALING)
#                 tile_sprite.center_x = grid_location.center_x * SPRITE_SCALING
#                 tile_sprite.center_y = grid_location.center_y * SPRITE_SCALING
#                 # print(f"{grid_location.tile.source} -- ({tile_sprite.center_x:4}, {tile_sprite.center_y:4})")
#                 sprite_list.append(tile_sprite)
#
#
# class MyGame(arcade.Window):
#     """ Main application class. """
#
#     def __init__(self, width, height):
#         """
#         Initializer
#         """
#         super().__init__(width, height)
#
#         file_path = os.path.dirname(os.path.abspath(__file__))
#         os.chdir(file_path)
#
#         # Sprite lists
#         self.all_sprites_list = None
#
#         # Set up the player
#         self.player_sprite = None
#         self.wall_list = None
#         self.floor_list = None
#         self.objects_list = None
#         self.player_list = None
#         self.view_bottom = 0
#         self.view_left = 0
#         self.my_map = None
#         self.lines = None
#
#     def setup(self):
#         """ Set up the game and initialize the variables. """
#
#         # Sprite lists
#         self.player_list = arcade.SpriteList()
#         self.wall_list = arcade.SpriteList()
#         self.floor_list = arcade.SpriteList()
#         self.objects_list = arcade.SpriteList()
#
#         # noinspection PyDeprecation
#         self.my_map = arcade.read_tiled_map(':resources:tmx_maps/isometric_dungeon.tmx', SPRITE_SCALING)
#
#         # Set up the player
#         self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png", 0.4)
#         px, py = arcade.isometric_grid_to_screen(self.my_map.width // 2,
#                                                  self.my_map.height // 2,
#                                                  self.my_map.width,
#                                                  self.my_map.height,
#                                                  self.my_map.tilewidth,
#                                                  self.my_map.tileheight)
#
#         self.player_sprite.center_x = px * SPRITE_SCALING
#         self.player_sprite.center_y = py * SPRITE_SCALING
#         self.player_list.append(self.player_sprite)
#
#         read_sprite_list(self.my_map.layers["Floor"], self.floor_list)
#         read_sprite_list(self.my_map.layers["Walls"], self.wall_list)
#         read_sprite_list(self.my_map.layers["Furniture"], self.wall_list)
#
#         # Set the background color
#         if self.my_map.backgroundcolor is None:
#             arcade.set_background_color(arcade.color.BLACK)
#         else:
#             arcade.set_background_color(self.my_map.backgroundcolor)
#
#         # Set the viewport boundaries
#         # These numbers set where we have 'scrolled' to.
#         self.view_left = 0
#         self.view_bottom = 0
#
#         self.lines = arcade.create_isometric_grid_lines(self.my_map.width // 2,
#                                                         self.my_map.height // 2,
#                                                         self.my_map.tilewidth,
#                                                         self.my_map.tileheight,
#                                                         arcade.color.BLACK, 4)
#
#     def on_draw(self):
#         """
#         Render the screen.
#         """
#
#         # This command has to happen before we start drawing
#         arcade.start_render()
#
#         # Draw all the sprites.
#         self.floor_list.draw()
#         self.player_list.draw()
#         self.wall_list.draw()
#         self.lines.draw()
#
#
# def test_main():
#     """ Main method """
#     window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
#     window.setup()
#     window.test()
#     window.close()
