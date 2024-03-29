import arcade
import tempfile
import os
from pathlib import Path


def test_save_screenshot_window(window: arcade.Window):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_1 = f'{temp_dir}/screen.png'
        file_2 = Path(temp_dir, 'screen2.png')
        window.save_screenshot(file_1)
        assert os.path.exists(file_1)

        window.save_screenshot(file_2)
        assert os.path.exists(file_2)
    

def test_command_with_location(window: arcade.Window):
    with tempfile.TemporaryDirectory() as temp_dir:
        file_1 = f'{temp_dir}/screen.png'
        file_2 = Path(temp_dir, 'screen2.png')
        arcade.save_screenshot(file_1)
        assert os.path.exists(file_1)

        window.save_screenshot(file_2)
        assert os.path.exists(file_2)
