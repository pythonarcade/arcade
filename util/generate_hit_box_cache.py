"""
Generates a cache of hit boxes for all the built in resources.
"""
import sys
import time
from pathlib import Path
import arcade
from arcade.cache.hit_box import HitBoxCache

RESOURCE_DIR = Path(__file__).parent.parent / "arcade" / "resources"
INCLUDE_SUFFIXES = set([".png", ".jpg", ".jpeg"])
DESTINATION_PATH = RESOURCE_DIR / "cache" / "hit_box_cache.json"
# DESTINATION_PATH = RESOURCE_DIR / "cache" / "hit_box_cache.json.gz"

time_start = time.time()

print()
print("Scanning directory for images:", RESOURCE_DIR)
print("Include suffixes:", INCLUDE_SUFFIXES)

ignored_suffixes = set()
image_paths = []

# Find resource files with the right suffix
for path in RESOURCE_DIR.glob("**/*"):
    if path.is_dir():
        continue
    if path.suffix in INCLUDE_SUFFIXES:
        image_paths.append(path)

    ignored_suffixes.add(path.suffix)

print("Found", len(image_paths), "images")

textures = []
# Load the images and generate the hit boxes
for path in image_paths:
    sys.stdout.write(".")
    sys.stdout.flush()
    algorithm = "simple"
    try:
        algorithm = "simple"
        textures.append(arcade.load_texture(path, hit_box_algorithm=algorithm))
        algorithm = "detailed"
        textures.append(arcade.load_texture(path, hit_box_algorithm=algorithm))    
    except Exception as e:
        print()
        print(f"Error loading ({algorithm}): {path.relative_to(RESOURCE_DIR)}")
        print(e)

sys.stdout.write("\n")
print("hit_box_cache", arcade.Texture.hit_box_cache)
print("Saving cache file to disk:", DESTINATION_PATH)
arcade.Texture.hit_box_cache.save(DESTINATION_PATH)

cache = HitBoxCache()
cache.load(DESTINATION_PATH)
if len(cache) != len(arcade.Texture.hit_box_cache):
    raise ValueError("ERROR: Cache file did not load correctly.")
else:
    print("Cache file loaded correctly.")

print("Ignored the following suffixes:", ignored_suffixes)
print("Duration:", time.time() - time_start, "seconds")
