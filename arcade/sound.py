import pyglet

# Special code for Windows so we grab the proper avbin from our directory.
# Otherwise hope the correct package is installed.
import os
if os.name == "nt":
	import site
	packages = site.getsitepackages()
	path = packages[0] + "/lib/site-packages/arcade/"
else:
	path = ""

pyglet.lib.load_library(path + 'avbin')
pyglet.have_avbin=True

def load_sound(filename):
	"""
	Load a sound and get it ready to play.

	>>> import arcade
	>>> my_sound = arcade.load_sound("examples/sounds/laser1.ogg")
	>>> arcade.play_sound(my_sound)
	"""
	source = pyglet.media.load(filename, streaming=False)
	return source

def play_sound(sound):
	"""
	Play a previously loaded sound.
	"""
	sound.play()
