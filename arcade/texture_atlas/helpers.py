# """
# THIS IS AN EXPERIMENTAL MODULE WITH NO GUARANTEES OF STABILITY OR SUPPORT.
# """
# from __future__ import annotations

# import json
# from pathlib import Path
# from time import perf_counter
# from typing import Dict, Tuple, cast

# import PIL.Image

# import arcade
# from arcade import cache
# from arcade.texture import ImageData, Texture

# from .atlas_2d import AtlasRegion, DefaultTextureAtlas


# class FakeImage:
#     """A fake PIL image"""
#     def __init__(self, size):
#         self.size = size

#     @property
#     def width(self):
#         return self.size[0]

#     @property
#     def height(self):
#         return self.size[1]


# def _dump_region_info(region: AtlasRegion):
#     return {
#         "pos": [region.x, region.y],
#         "size": [region.width, region.height],
#         "uvs": region.texture_coordinates,
#     }


# def save_atlas(atlas: DefaultTextureAtlas, directory: Path, name: str, resource_root: Path):
#     """
#     Dump the atlas to a file. This includes the atlas image
#     and metadata.

#     :param atlas: The atlas to dump
#     :param directory: The directory to dump the atlas to
#     :param name: The name of the atlas
#     """
#     # Dump the image
#     atlas.save(directory / f"{name}.png", flip=False)

#     meta = {
#         'name': name,
#         'atlas_file': f"{name}.png",
#         'size': atlas.size,
#         'border': atlas.border,
#         'textures': [],
#         'images': [],
#     }
#     # Images
#     images = []
#     for image in atlas._images:
#         images.append({
#             "hash": image.hash,
#             "region": _dump_region_info(atlas.get_image_region_info(image.hash)),
#         })
#     meta['images'] = images

#     # Textures
#     textures = []
#     for texture in atlas.textures:
#         if texture.file_path  is None:
#             raise ValueError("Can't save a texture not loaded from a file")

#         textures.append({
#             "hash": texture.image_data.hash,
#             "path": texture.file_path.relative_to(resource_root).as_posix(),
#             "crop": texture.crop_values,
#             "points": texture.hit_box_points,
#             "region": _dump_region_info(atlas.get_texture_region_info(texture.atlas_name)),
#             "vertex_order": texture._vertex_order,
#         })

#     meta['textures'] = textures

#     # Dump the metadata
#     with open(directory / f"{name}.json", 'w') as fd:
#         json.dump(meta, fd, indent=2)


# def load_atlas(
#     meta_file: Path,
#     resource_root: Path
# ) -> Tuple[TextureAtlas, Dict[str, float]]:
#     """
#     Load a texture atlas from disk.
#     """
#     ctx = arcade.get_window().ctx
#     perf_data = {}

#     t = perf_counter()
#     # Load metadata
#     with open(meta_file, 'r') as fd:
#         meta = json.load(fd)
#     perf_data['load_meta'] = perf_counter() - t

#     t = perf_counter()
#     atlas = DefaultTextureAtlas(
#         meta['size'],
#         border=meta["border"],
#         auto_resize=False,
#     )
#     perf_data['create_atlas'] = perf_counter() - t

#     # Inject the atlas image
#     t = perf_counter()
#     atlas._texture = ctx.load_texture(meta['atlas_file'], flip=False)
#     atlas._fbo = ctx.framebuffer(color_attachments=[atlas._texture])
#     perf_data['load_texture'] = perf_counter() - t

#     # Recreate images
#     t = perf_counter()
#     image_map: Dict[str, ImageData] = {}
#     for im in meta['images']:
#         image_data = ImageData(
#             cast(PIL.Image.Image, FakeImage(im['region']['size'])),
#             im['hash'],
#         )
#         atlas._images.add(image_data)
#         image_map[image_data.hash] = image_data
#         # cache.image_data_cache.put()
#         region = AtlasRegion(
#             atlas,
#             im['region']['pos'][0],
#             im['region']['pos'][1],
#             im['region']['size'][0],
#             im['region']['size'][1],
#             tuple(im['region']['uvs']),  # type: ignore
#         )
#         atlas._image_regions[image_data.hash] = region
#         # Get a slot for the image and write the uv data
#         slot = atlas._image_uv_slots_free.popleft()
#         atlas._image_uv_slots[image_data.hash] = slot
#         for i in range(8):
#             atlas._image_uv_data[slot * 8 + i] = region.texture_coordinates[i]

#     perf_data['create_images'] = perf_counter() - t

#     # Recreate textures
#     t = perf_counter()
#     for tex in meta['textures']:
#         texture = Texture(
#             image_map[tex['hash']],
#             hit_box_points=tex['points'],
#         )
#         texture._vertex_order = tuple(tex['vertex_order'])  # type: ignore
#         texture._update_cache_names()
#         atlas._textures[texture.atlas_name] = texture
#         # Cache the texture strongly so it doesn't get garbage collected
#         cache.texture_cache.put(texture, file_path=resource_root / tex['hash'])
#         texture.file_path = resource_root / tex['path']
#         texture.crop_values = tex['crop']
#         region = AtlasRegion(
#             atlas,
#             tex['region']['pos'][0],
#             tex['region']['pos'][1],
#             tex['region']['size'][0],
#             tex['region']['size'][1],
#             tuple(tex['region']['uvs']),  # type: ignore
#         )
#         atlas._texture_regions[texture.atlas_name] = region
#         # Get a slot for the image and write the uv data
#         slot = atlas._texture_uv_slots_free.popleft()
#         atlas._texture_uv_slots[texture.atlas_name] = slot
#         for i in range(8):
#             atlas._texture_uv_data[slot * 8 + i] = region.texture_coordinates[i]

#     perf_data['create_textures'] = perf_counter() - t

#     # Write the uv data to vram
#     atlas.use_uv_texture()

#     return atlas, perf_data
#     return atlas, perf_data
