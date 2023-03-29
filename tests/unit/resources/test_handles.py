from pathlib import Path
import pytest
import arcade
from arcade import resources

MODULE_DIR = Path(__file__).parent.parent.resolve()


def test_default_handles():
    """Test if we can find resources through system and resources handles"""
    assert len(resources.handles) >= 2
    resources.resolve(":system:gamecontrollerdb.txt")
    resources.resolve(":resources:gamecontrollerdb.txt")

    # Ww can't find an asset using a system handle
    resources.resolve(":resources:images/cards/cardBack_blue1.png")
    with pytest.raises(FileNotFoundError):
        resources.resolve(":system:images/cards/cardBack_blue1.png")


def test_add_handles(monkeypatch):
    monkeypatch.setattr(resources, "handles", {})

    # Ensure no duplicate paths in the same handler
    resources.add_resource_handle("test", MODULE_DIR)
    resources.add_resource_handle("test", MODULE_DIR)
    assert len(resources.get_resource_handle_paths("test")) == 1

    # We don't allow relative paths in handles
    with pytest.raises(RuntimeError, match="must be absolute"):
        resources.add_resource_handle("test", "moo")

    # We don't allow non-existent paths in handles
    with pytest.raises(FileNotFoundError, match="does not exist"):
        resources.add_resource_handle("test", MODULE_DIR / "moo")


def test_misc():
    path = resources.resolve(":resources:images/cards/cardBack_blue1.png")
    assert resources.resolve(path) == path

