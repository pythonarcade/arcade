"""
Sound Demo

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.sound
"""
import arcade

arcade.open_window(300, 300, "Sound Demo")
laser_sound = arcade.load_sound("sounds/laser1.wav")
arcade.play_sound(laser_sound)
arcade.run()