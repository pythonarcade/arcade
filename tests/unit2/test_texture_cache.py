import arcade


def _gen_cache_name(path, x, y, w, h):
    pass


def test_load_texture():
    """Check cache for load_texture"""
    arcade.cleanup_texture_cache()
    path = ":resources:images/test_textures/test_texture.png"
    name = _gen_cache_name(path, 0, 0, 0, 0)

    # Load texture twice and check the cache name
    # t = arcade.load_texture(path)
    # assert t.name == name
    # t = arcade.load_texture(path)
    # assert t.name == name

    # # Load sub-section and check cache name
    # t1 = arcade.load_texture(path)
    # assert t1.name == name
    # t2 = arcade.load_texture(path)
    # t3 = arcade.load_texture(path)
    # t4 = arcade.load_texture(path)
