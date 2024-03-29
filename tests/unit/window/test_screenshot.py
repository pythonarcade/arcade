import arcade
import glob
import os


def test_no_location(window: arcade.Window):
    filepath = window.save_screenshot()
    assert filepath
    os.remove(filepath)
    

def test_location(window: arcade.Window):
    filepath = window.save_screenshot('doc/')
    assert filepath
    os.remove(filepath)


def test_command(window: arcade.Window):
    filepath = arcade.save_screenshot()
    assert filepath
    os.remove(filepath)


def test_command_with_location(window: arcade.Window):
    filepath = arcade.save_screenshot('doc')
    assert filepath
    os.remove(filepath)
