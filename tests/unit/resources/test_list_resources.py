"""
List and count built-in assets in arcade.

Leave +-10 margin on the count to allow minor changes.
"""

import pytest
import arcade


def test_all():
    resources = arcade.resources.list_built_in_assets()
    assert len(resources) == pytest.approx(770, abs=10)


def test_png():
    resources = arcade.resources.list_built_in_assets(extensions=(".png",))
    assert len(resources) == pytest.approx(630, abs=10)


def test_audio():
    resources = arcade.resources.list_built_in_assets(
        extensions=(".wav", ".ogg", ".mp3"),
    )
    assert len(resources) == pytest.approx(60, abs=10)
