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


def test_resolve_create(tmp_path):
    """Test if we can create directories and files using the resolve."""
    # Test directory creation
    new_dir = tmp_path / "created_dir"
    assert not new_dir.exists()
    result_dir = resources.resolve(new_dir, create=True)
    assert result_dir == new_dir.resolve()
    assert new_dir.exists() and new_dir.is_dir()

    # Test file creation
    new_file = tmp_path / "created_file.txt"
    assert not new_file.exists()
    result_file = resources.resolve(new_file, create=True)
    assert result_file == new_file.resolve()
    assert new_file.exists() and new_file.is_file()


def test_default_handle_create():
    """Test if we can create directories and files using the default handle."""
    handle_dir = ":resources:new_dir"
    with pytest.raises(FileNotFoundError):
        resources.resolve(handle_dir)
    result_dir = resources.resolve(handle_dir, create=True)
    assert result_dir.exists() and result_dir.is_dir()
    for base_path in resources.get_resource_handle_paths("resources"):
        dir_path = base_path / "new_dir"
        if dir_path.exists() and dir_path.is_dir():
            dir_path.rmdir()


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
