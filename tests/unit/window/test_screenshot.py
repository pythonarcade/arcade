import arcade
import glob
import os

def test_no_location(window: arcade.Window):
    window.save_screenshot()
    file_list = glob.glob('testing_*.png')
    assert file_list
    os.remove(file_list[0])
    

def test_location(window: arcade.Window):
    window.save_screenshot('doc/')
    file_list =  glob.glob('doc/testing_*.png')
    assert file_list
    os.remove(file_list[0])

def test_command(window: arcade.Window):
    arcade.save_screenshot()
    file_list =  glob.glob('testing_*.png')
    assert file_list
    os.remove(file_list[0])

def test_command_with_location(window: arcade.Window):
    arcade.save_screenshot('doc')
    file_list =  glob.glob('doc/testing_*.png')
    assert file_list
    os.remove(file_list[0])
