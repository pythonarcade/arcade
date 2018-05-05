import arcade
import time

print("Testing .wav")
try:
    my_sound = arcade.load_sound("laser1.wav")
    arcade.play_sound(my_sound)
except Exception as e:
    print(e)

time.sleep(1)
print("Done with .wav test")
print()

print("Testing .mp3")
try:
    my_sound = arcade.load_sound("laser1.mp3")
    arcade.play_sound(my_sound)
except Exception as e:
    print(e)

time.sleep(1)
print("Done with .mp3 test")
print()

print("Testing .ogg")
try:
    my_sound = arcade.load_sound("laser1.ogg")
    arcade.play_sound(my_sound)
except Exception as e:
    print(e)

time.sleep(1)
print("Done with .ogg test")
print()

