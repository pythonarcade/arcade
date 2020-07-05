"""
Tests if examples render and show the same screen like expected
"""
import os
import sys
from importlib import import_module
from pathlib import Path

import pkg_resources
import pytest

import arcade
from . import T


@pytest.fixture
def window():
    window = arcade.Window(title='ARCADE_GUI')
    yield window
    window.close()


def view_to_png(window: arcade.Window, view: arcade.View, path: Path):
    window.clear()

    window.show_view(view)
    window.dispatch_event('on_draw')
    window.dispatch_events()

    arcade.finish_render()
    arcade.get_image().save(str(path))


def files_equal(file1: Path, file2: Path):
    return file1.read_bytes() == file2.read_bytes()


def load_view(abs_module_path) -> arcade.View:
    module_object = import_module(abs_module_path)
    target_class = getattr(module_object, 'MyView')

    assert isinstance(target_class, arcade.View)
    return target_class


@pytest.mark.skipif(os.getenv('TRAVIS') == 'true',
                    reason=('Example tests not executable on travis, '
                            'check https://travis-ci.org/github/eruvanos/arcade_gui/jobs/678758144#L506'))
@pytest.mark.skipif(sys.platform == 'darwin', reason='Not yet supported on darwin')
@pytest.mark.parametrize('example', [
    T('show_id_example', 'show_id_example'),
    T('show_uiinputbox', 'show_uiinputbox'),
    T('show_uilabel', 'show_uilabel'),
    T('show_uiflatbutton', 'show_uiflatbutton'),
    T('show_all', 'show_all'),
    T('show_uiflatbutton_custom_style', 'show_uiflatbutton_custom_style')
])
def test_id_example(window, example):
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
    assert files_equal(expected_screen, actual_screen)
    actual_screen.unlink()
