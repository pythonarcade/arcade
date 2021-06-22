from arcade import TextureAtlas, Texture


def test_create(ctx):
    TextureAtlas((100, 100), border=1)
    TextureAtlas((100, 200), border=0)


def test_add(ctx):
    atlas = TextureAtlas((100, 100), border=1)


def test_remove(ctx):
    pass
