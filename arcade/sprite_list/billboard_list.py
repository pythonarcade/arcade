from __future__ import annotations
from arcade.sprite_list import SpriteList


__all__ = ("BillboardList",)


class BillboardList(SpriteList):
    """
    The purpose of the BillboardList is to batch draw a list of sprites.
    The difference between the BillboardList and a basic SpriteList is how it
    orientates Sprites. The normal SpriteList always aligns them to the X-Y plane.
    The BillboardList purposely forces the sprite to always look directly towards
    the screen.

    It is not recommended to do collision checking with a billboardlist as the collisions
    still happen in the X-Y plane.

    For the advanced options check the advanced section in the
    arcade documentation.

    :param use_spatial_hash: If set to True, this will make creating a sprite, and
            moving a sprite
            in the SpriteList slower, but it will speed up collision detection
            with items in the SpriteList. Great for doing collision detection
            with static walls/platforms in large maps.
    :param spatial_hash_cell_size: The cell size of the spatial hash (default: 128)
    :param atlas: (Advanced) The texture atlas for this sprite list. If no
            atlas is supplied the global/default one will be used.
    :param capacity: (Advanced) The initial capacity of the internal buffer.
            It's a suggestion for the maximum amount of sprites this list
            can hold. Can normally be left with default value.
    :param lazy: (Advanced) ``True`` delays creating OpenGL resources
            for the sprite list until either its :py:meth:`~SpriteList.draw`
            or :py:meth:`~SpriteList.initialize` method is called. See
            :ref:`pg_spritelist_advanced_lazy_spritelists` to learn more.
    :param visible: Setting this to False will cause the SpriteList to not
            be drawn. When draw is called, the method will just return without drawing.
    """

    def _init_deferred(self) -> None:
        super()._init_deferred()
        self.program = self.ctx.billboard_list_program_no_cull
