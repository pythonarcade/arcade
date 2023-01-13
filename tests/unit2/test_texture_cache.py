from arcade.cache import TextureCacheEntry


def test_texture_cache_entry():
    tce = TextureCacheEntry(
        name="test",
        xy=(0, 0),
        size=(10, 10),
        hit_box_algorithm="simple",
        hit_box_detail=1.0,
        vertex_order=(0, 1, 2, 3),
    )
    assert tce.name == "test"
    assert tce.xy == (0, 0)
    assert tce.size == (10, 10)
    assert tce.hit_box_algorithm == "simple"
    assert tce.hit_box_detail == 1.0
    assert tce.vertex_order == (0, 1, 2, 3)
    assert str(tce) == "test|0|0|10|10|simple|1.0|0|1|2|3"
    assert TextureCacheEntry.from_str(str(tce)) == tce


# def test_load_texture():
#     """Check cache for load_texture"""
#     arcade.cleanup_texture_cache()
#     path = ":resources:images/test_textures/test_texture.png"
#     name = _gen_cache_name(path, 0, 0, 0, 0)

#     # Load texture twice and check the cache name
#     # t = arcade.load_texture(path)
#     # assert t.name == name
#     # t = arcade.load_texture(path)
#     # assert t.name == name

#     # # Load sub-section and check cache name
#     # t1 = arcade.load_texture(path)
#     # assert t1.name == name
#     # t2 = arcade.load_texture(path)
#     # t3 = arcade.load_texture(path)
#     # t4 = arcade.load_texture(path)
