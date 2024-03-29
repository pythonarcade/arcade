import arcade
import glob
import os
import pathlib


def test_no_location(window: arcade.Window):
    filepath = window.save_screenshot()
    assert filepath
    os.remove(filepath)
    

def test_location(window: arcade.Window):
    path = pathlib.Path().parent.parent.absolute()
    filepath = window.save_screenshot(str(path))
    assert filepath
    os.remove(filepath)


def test_command(window: arcade.Window):
    filepath = arcade.save_screenshot()
    assert filepath
    os.remove(filepath)


def test_command_with_location(window: arcade.Window):
    path = pathlib.Path().parent.parent.absolute()
    filepath = arcade.save_screenshot(str(path))
    assert filepath
    os.remove(filepath)
