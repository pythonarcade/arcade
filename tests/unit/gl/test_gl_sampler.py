from arcade import ArcadeContext


def test_create(ctx: ArcadeContext):
    texture = ctx.texture((10, 10))
    sampler = ctx.sampler(texture)
    assert sampler.texture == texture
    # defaults
    assert sampler.wrap_x == ctx.REPEAT
    assert sampler.wrap_y == ctx.REPEAT
    assert sampler.filter == (ctx.LINEAR, ctx.LINEAR)
    assert sampler.anisotropy == 1.0
