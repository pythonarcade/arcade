import arcade


def test_default_handles():
    """Test if we can find resources through system and resources handles"""
    arcade.resources.resolve(":system:gamecontrollerdb.txt")
    arcade.resources.resolve(":resources:gamecontrollerdb.txt")
