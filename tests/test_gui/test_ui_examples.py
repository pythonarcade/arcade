"""
Tests if examples render and show the same screen like expected
"""
import os
from importlib import import_module
from pathlib import Path

import numpy as np
import pkg_resources
import pytest
from PIL import Image

import arcade

from . import T


@pytest.fixture
def window():
    window = arcade.Window(title='ARCADE_GUI')
    yield window
    window.close()


def view_to_png(window: arcade.Window, view: arcade.View, path: Path):
    # window.clear()
    ctx = window.ctx
    offscreen = ctx.framebuffer(color_attachments=[ctx.texture(window.get_size(), components=4)])
    offscreen.clear()
    offscreen.use()
    window.show_view(view)
    window.dispatch_event('on_draw')
    window.dispatch_events()

    ctx.finish()
    image = Image.frombuffer('RGBA', offscreen.size, offscreen.read(components=4)).convert('RGB')
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    image.save(str(path))
    # arcade.get_image().convert('RGB').save(str(path))
    ctx.screen.use()


def files_equal(file1: Path, file2: Path):
    return file1.read_bytes() == file2.read_bytes()


def img_diff(file1: Path, file2: Path) -> float:
    """Difference between two images in percent"""
    img_a = Image.open(file1).convert('RGB')
    img_b = Image.open(file2).convert('RGB')
    a = np.frombuffer(img_a.tobytes(), dtype='u1').astype('f4')
    b = np.frombuffer(img_b.tobytes(), dtype='u1').astype('f4')
    r = np.absolute(a - b)
    # save diff
    # Image.frombytes('RGB', (800, 600), r.astype('u1')).save(file2)
    print(np.sum(r), np.sum(a))
    return np.sum(r) / np.sum(a)


def load_view(abs_module_path) -> arcade.View:
    module_object = import_module(abs_module_path)
    target_class = getattr(module_object, 'MyView')

    assert isinstance(target_class, arcade.View)
    return target_class


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason=('Example tests not executable on travis, '
                            'check https://travis-ci.org/github/eruvanos/arcade_gui/jobs/678758144#L506'))
@pytest.mark.parametrize('example', [
    T('show_id_example', 'show_id_example'),
    T('show_uiinputbox', 'show_uiinputbox'),
    T('show_uilabel', 'show_uilabel'),
    T('show_uiflatbutton', 'show_uiflatbutton'),
    T('show_all', 'show_all'),
    T('show_uiflatbutton_custom_style', 'show_uiflatbutton_custom_style')
])
def test_id_example(twm, window, example):
    expected_screen = Path(pkg_resources.resource_filename('tests.test_gui', f'assets/{example}.png'))

    # import example view
    MyView = import_module(f'arcade.gui.examples.{example}').MyView
    view = MyView(window)

    # Render View and take screen shot
    actual_screen = expected_screen.with_name(f'{example}_tmp.png')
    view_to_png(window, view, actual_screen)

    # manually clean up ui_manager handlers
    # TODO this should be handled by arcade
    window.remove_handlers(view.ui_manager)

    # compare files
    assert expected_screen.exists(), f'expected screen missing, actual at {actual_screen}'

    if not twm:
        assert img_diff(expected_screen, actual_screen) < 0.135  # max threshold for image difference, mac vs win
        actual_screen.unlink()
