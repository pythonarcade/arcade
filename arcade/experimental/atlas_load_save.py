# """
# Quick and dirty atlas load/save testing.
# Loading and saving atlases are not officially supported.
# This is simply an experiment.

# Dump atlas:
# python arcade/experimental/atlas_load_save.py save

# Load atlas:
# python arcade/experimental/atlas_load_save.py load
# """

# from __future__ import annotations

# import sys
# import math
# import pprint
# from typing import Dict, Tuple, List
# from time import perf_counter
# from pathlib import Path
# import arcade
# from arcade.texture_atlas.helpers import save_atlas, load_atlas

# MODE = 'save'
# RESOURCE_ROOT = arcade.resources.ASSET_PATH
# DESTINATION = Path.cwd()

# texture_paths: List[Path] = []
# texture_paths += RESOURCE_ROOT.glob("images/enemies/*.png")
# texture_paths += RESOURCE_ROOT.glob("images/items/*.png")
# texture_paths += RESOURCE_ROOT.glob("images/alien/*.png")
# texture_paths += RESOURCE_ROOT.glob("images/tiles/*.png")


# def populate_atlas(atlas: arcade.TextureAtlas) -> Tuple[int, Dict[str, float]]:
#     """Populate the atlas with all the resources we can find"""
#     perf_data = {}
#     textures = []
#     t = perf_counter()
#     for path in texture_paths:
#         texture = arcade.load_texture(path, hit_box_algorithm=arcade.hitbox.algo_simple)
#         textures.append(texture)
#     perf_data['load_textures'] = perf_counter() - t

#     t = perf_counter()
#     for texture in textures:
#         atlas.add(texture)
#     perf_data['add_textures'] = perf_counter() - t

#     return len(textures), perf_data


# class AtlasLoadSave(arcade.Window):
#     """
#     This class demonstrates how to load and save texture atlases.
#     """

#     def __init__(self):
#         super().__init__(1280, 720, "Atlas Load Save")
#         self.done = False

#         if MODE == "save":
#             t = perf_counter()
#             self.atlas = arcade.TextureAtlas((1024, 1024))
#             count, perf_data = populate_atlas(self.atlas)
#             print(f'Populated atlas with {count} texture in {perf_counter() - t:.2f} seconds')
#             save_atlas(
#                 self.atlas,
#                 directory=Path.cwd(),
#                 name="test",
#                 resource_root=RESOURCE_ROOT,
#             )
#             self.done = True
#         if MODE == "load":
#             t = perf_counter()
#             self.atlas, perf_data = load_atlas(Path.cwd() / 'test.json', RESOURCE_ROOT)
#             print(f'Loaded atlas in {perf_counter() - t:.2f} seconds')
#             pprint.pprint(perf_data, indent=2)
#             # self.done = True

#         # Make a sprite for each texture
#         self.sp = arcade.SpriteList(atlas=self.atlas)
#         for i, texture in enumerate(self.atlas.textures):
#             pos = i * 64
#             sprite = arcade.Sprite(
#                 texture,
#                 center_x=32 + math.fmod(pos, self.width),
#                 center_y=32 + math.floor(pos / self.width) * 64,
#                 scale=0.45,
#             )
#             self.sp.append(sprite)

#         print(f'Atlas has {len(self.atlas._textures)} textures')

#         # self.atlas.show(draw_borders=True)

#     def on_draw(self):
#         self.clear()
#         self.sp.draw(pixelated=True)

#     def on_update(self, delta_time: float):
#         if self.done:
#             self.close()


# if len(sys.argv) < 2 or sys.argv[1] not in ('load', 'save'):
#     print('Usage: atlas_load_save.py [save|load]')
#     sys.exit(1)

# MODE = sys.argv[1]

# AtlasLoadSave().run()
