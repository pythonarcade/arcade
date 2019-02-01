"""
Sound Demo

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sound
"""
import arcade
import os

# Set the working directory (where we expect to find files) to the same
# directory this .py file is in. You can leave this out of your own
# code, but it is needed to easily run the examples using "python -m"
# as mentioned at the top of this program.
file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)

arcade.open_window(300, 300, "Sound Demo")
laser_sound = arcade.load_sound("sounds/laser1.wav")
arcade.play_sound(laser_sound)
arcade.run()