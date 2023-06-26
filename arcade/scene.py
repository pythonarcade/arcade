"""
This module provides a Scene class which acts as a sprite list manager.

It allows you to do the following:

* Group sprite lists into a larger object, using them like layers
* Draw & update the contained sprite lists
* Add sprites by name
* Load from tiled map objects
* Control sprite list draw order within the group
"""

from typing import Dict, List, Optional, Union, Iterable, Tuple

from arcade import Sprite, SpriteList
from arcade.types import Color, RGBA255
from arcade.tilemap import TileMap

from warnings import warn

__all__ = ["Scene", "SceneKeyError"]


class SceneKeyError(KeyError):
    """
    Raised when a py:class:`.Scene` cannot find a layer for a specified name.

    It is a subclass of :py:class:`KeyError`, and you can handle it as
    one if you wish::

        try:
            # this will raise a SceneKeyError
            scene_instance.add_sprite("missing_layer_name", arcade.SpriteSolidColor(10,10))

        # We can handle it as a KeyError because it is a subclass of it
        except KeyError as e:
            print("Your error handling should go here")

    The main purpose of this class is to help arcade's developers keep
    error messages consistent.

    :param name: the name of the missing :py:class:`~arcade.SpriteList`
    """

    def __init__(self, name: str):
        super().__init__(f"This scene does not contain a SpriteList named {name!r}.")
        self.layer_name = name


class Scene:
    """
    Stores :py:class:`~arcade.SpriteList` instances as named layers, allowing bulk updates & drawing.

    In addition to helping you update or draw multiple sprite lists at
    once, this class also provides the following convenience methods:

    * :py:meth:`.add_sprite`, which adds sprites to layers by name
    * :py:meth:`.Scene.from_tilemap`, which creates a scene from a
      :py:class:`~arcade.tilemap.TileMap` already loaded from tiled data
    * Fine-grained convenience methods for adding, deleting, and reordering
      sprite lists
    * Flexible but slow general convenience methods
    * Flexible but slow support for the ``in`` & ``del`` Python keywords.

    For another example of how to use this class, see :ref:`platformer_part_three`.
    """

    def __init__(self) -> None:
        self._sprite_lists: List[SpriteList] = []
        self._name_mapping: Dict[str, SpriteList] = {}

    def __len__(self) -> int:
        """
        Return the number of sprite lists in this scene.
        """
        return len(self._sprite_lists)

    def __delitem__(self, sprite_list: Union[int, str, SpriteList]) -> None:
        """
        Remove a sprite list from this scene by its index, name, or instance value.

        .. tip:: Use a more specific method when speed is important!

                 This method uses :py:func:`isinstance`, which will
                 slow down your program if used frequently!

        Consider the following alternatives:

        * :py:meth:`.remove_sprite_list_by_index`
        * :py:meth:`.remove_sprite_list_by_name`
        * :py:meth:`.remove_sprite_list_by_object`

        :param sprite_list:
            The index, name, or :py:class:`~arcade.SpriteList` instance to remove from
            this scene.
        """
        if isinstance(sprite_list, int):
            self.remove_sprite_list_by_index(sprite_list)
        elif isinstance(sprite_list, str):
            self.remove_sprite_list_by_name(sprite_list)
        else:
            self.remove_sprite_list_by_object(sprite_list)

    @classmethod
    def from_tilemap(cls, tilemap: TileMap) -> "Scene":
        """
        Create a new Scene from a :py:class:`~arcade.tilemap.TileMap` object.

        The SpriteLists will use the layer names and ordering as defined in the
        Tiled file.

        :param tilemap: The :py:class:`~arcade.tilemap.TileMap`
            object to create the scene from.
        """
        scene = cls()
        for name, sprite_list in tilemap.sprite_lists.items():
            scene.add_sprite_list(name=name, sprite_list=sprite_list)
        return scene

    def get_sprite_list(self, name: str) -> SpriteList:
        """
        Retrieve a sprite list by name.

        It is also possible to access sprite lists the following ways:

        * ``scene_instance[name]``
        * directly accessing ``scene_instance._name_mapping``, although this will
          get flagged by linters as bad style.

        :param name: The name of the sprite list to retrieve.
        """
        return self._name_mapping[name]

    def __getitem__(self, key: str) -> SpriteList:
        """
        Retrieve a sprite list by name.

        This is here for ease of use to make sub-scripting the scene object directly
        to retrieve a SpriteList possible.

        :param key: The name of the sprite list to retrieve
        """
        if key in self._name_mapping:
            return self._name_mapping[key]

        raise SceneKeyError(key)

    def add_sprite(self, name: str, sprite: Sprite) -> None:
        """
        Add a Sprite to the SpriteList with the specified name.

        If there is no SpriteList for the given ``name``, one will be
        created with :py:class:`SpriteList`'s default arguments and
        added to the end (top) of the scene's current draw order.

        To fully customize the SpriteList's options, you should create
        it directly and add it to the scene with one of the following:

        * :py:meth:`.add_sprite_list_before`
        * :py:meth:`.add_sprite_list`
        * :py:meth:`.add_sprite_list_after`

        :param name: The name of the sprite list to add to or create.
        :param sprite: The sprite to add.
        """
        if name in self._name_mapping:
            self._name_mapping[name].append(sprite)
        else:
            new_list: SpriteList = SpriteList()
            new_list.append(sprite)
            self.add_sprite_list(name=name, sprite_list=new_list)

    def add_sprite_list(
        self,
        name: str,
        use_spatial_hash: bool = False,
        sprite_list: Optional[SpriteList] = None,
    ) -> None:
        """
        Add a SpriteList to the scene with the specified name.

        This will add a new SpriteList as a layer above the others in the scene.

        If no SpriteList is supplied via the ``sprite_list`` parameter then a new one will be
        created, and the ``use_spatial_hash`` parameter will be respected for that creation.

        :param name: The name to give the new layer.
        :param use_spatial_hash: If creating a new sprite list, whether
            to enable spatial hashing on it.
        :param sprite_list: Use a specific sprite list rather than creating a new one.
        """
        if sprite_list is None:
            sprite_list = SpriteList(use_spatial_hash=use_spatial_hash)
        if name in self._name_mapping.keys():
            self.remove_sprite_list_by_name(name)
            warn("A Spritelist with the name: "+name+", is already in the scene, will override Spritelist")
        self._name_mapping[name] = sprite_list
        self._sprite_lists.append(sprite_list)

    def add_sprite_list_before(
        self,
        name: str,
        before: str,
        use_spatial_hash: bool = False,
        sprite_list: Optional[SpriteList] = None,
    ) -> None:
        """
        Add a sprite list to the scene with the specified name before another SpriteList.

        If no sprite list is supplied via the ``sprite_list`` parameter, then a new one
        will be created. Aside from the value of ``use_spatial_hash`` passed to this
        method, it will use the default arguments for a new :py:class:`SpriteList`.

        The added sprite list will be drawn under the sprite list named in ``before``.

        :param name: The name to give the new layer.
        :param before: The name of the layer to place the new
            one before.
        :param use_spatial_hash: If creating a new sprite list, selects
            whether to enable spatial hashing.
        :param sprite_list: If a sprite list is passed via
            this argument, it will be used instead of creating a new one.
        """
        if sprite_list is None:
            sprite_list = SpriteList(use_spatial_hash=use_spatial_hash)
        if name in self._name_mapping.keys():
            self.remove_sprite_list_by_name(name)
            warn("A Spritelist with the name: "+name+", is already in the scene, will override Spritelist")
        self._name_mapping[name] = sprite_list
        before_list = self._name_mapping[before]
        index = self._sprite_lists.index(before_list)
        self._sprite_lists.insert(index, sprite_list)

    def move_sprite_list_before(
        self,
        name: str,
        before: str,
    ) -> None:
        """
        Move a named SpriteList in the scene to be before another SpriteList in the scene.

        A :py:class:`~arcade.scene.SceneKeyError` will be raised if either ``name``
        or ``before`` contain a name not currently in the scene. This exception can
        be handled as a :py:class:`KeyError`.

        :param name: The name of the SpriteList to move.
        :param before: The name of the SpriteList to place it before.
        """
        if name not in self._name_mapping:
            raise SceneKeyError(name)

        if before not in self._name_mapping:
            raise SceneKeyError(before)

        name_list = self._name_mapping[name]
        before_list = self._name_mapping[before]
        new_index = self._sprite_lists.index(before_list)
        old_index = self._sprite_lists.index(name_list)
        self._sprite_lists.insert(new_index, self._sprite_lists.pop(old_index))

    def add_sprite_list_after(
        self,
        name: str,
        after: str,
        use_spatial_hash: bool = False,
        sprite_list: Optional[SpriteList] = None,
    ) -> None:
        """
        Add a SpriteList to the scene with the specified name after a specific SpriteList.

        If no sprite list is supplied via the ``sprite_list`` parameter, then a new one
        will be created. Aside from the value of ``use_spatial_hash`` passed to this
        method, it will use the default arguments for a new :py:class:`SpriteList`.

        The added sprite list will be drawn above the sprite list named in ``after``.

        :param name: The name to give the layer.
        :param after: The name of the layer to place the new one after.
        :param use_spatial_hash: If creating a new sprite list, selects
            whether to enable spatial hashing.
        :param sprite_list: If a sprite list is passed via
            this argument, it will be used instead of creating a new one.
        """
        if sprite_list is None:
            sprite_list = SpriteList(use_spatial_hash=use_spatial_hash)
        if name in self._name_mapping.keys():
            self.remove_sprite_list_by_name(name)
            warn("A Spritelist with the name: "+name+", is already in the scene, will override Spritelist")
        self._name_mapping[name] = sprite_list
        after_list = self._name_mapping[after]
        index = self._sprite_lists.index(after_list) + 1
        self._sprite_lists.insert(index, sprite_list)

    def move_sprite_list_after(
        self,
        name: str,
        after: str,
    ) -> None:
        """
        Move a named SpriteList in the scene to be after another SpriteList in the scene.

        A :py:class:`~arcade.scene.SceneKeyError` will be raised if either ``name``
        or ``after`` contain a name not currently in the scene. This exception can
        be handled as a :py:class:`KeyError`.

        :param name: The name of the SpriteList to move.
        :param after: The name of the SpriteList to place it after.
        """
        if name not in self._name_mapping:
            raise SceneKeyError(name)

        if after not in self._name_mapping:
            raise SceneKeyError(after)

        name_list = self._name_mapping[name]
        after_list = self._name_mapping[after]
        new_index = self._sprite_lists.index(after_list) + 1
        old_index = self._sprite_lists.index(name_list)
        self._sprite_lists.insert(new_index, self._sprite_lists.pop(old_index))

    def remove_sprite_list_by_index(
        self,
        index: int
    ) -> None:
        """
        Remove a layer from the scene by its index in the draw order.

        :param index: The index of the sprite list to remove.
        """
        self.remove_sprite_list_by_object(self._sprite_lists[index])

    def remove_sprite_list_by_name(
        self,
        name: str,
    ) -> None:
        """
        Remove a layer from the scene by its name.

        A :py:class:`KeyError` will be raised if the SpriteList is not
        in the scene.

        :param name: The name of the sprite list to remove.
        """
        sprite_list = self._name_mapping[name]
        self._sprite_lists.remove(sprite_list)
        del self._name_mapping[name]

    def remove_sprite_list_by_object(self, sprite_list: SpriteList) -> None:
        """
        Remove the passed SpriteList instance from the Scene.

        A :py:class:`ValueError` will be raised if the passed sprite
        list is not in the scene.

        :param sprite_list: The sprite list to remove.
        """
        self._sprite_lists.remove(sprite_list)
        self._name_mapping = {
            key: val for key, val in self._name_mapping.items() if val != sprite_list
        }

    def update(self, names: Optional[Iterable[str]] = None) -> None:
        """
        Call :py:meth:`~arcade.SpriteList.update` on the scene's sprite lists.

        By default, this method calls :py:meth:`~arcade.SpriteList.update`
        on the scene's sprite lists in the default draw order.

        You can limit and reorder the updates with the ``names``
        argument by passing a list of names in the scene. The sprite
        lists will be drawn in the order of the passed iterable. If a
        name is not in the scene, a :py:class:`KeyError` will be raised.

        :param names: Which layers & what order to update them in.
        """
        if names:
            for name in names:
                self._name_mapping[name].update()
            return

        for sprite_list in self._sprite_lists:
            sprite_list.update()

    def on_update(self, delta_time: float = 1 / 60, names: Optional[Iterable[str]] = None) -> None:
        """
        Call :py:meth:`~arcade.SpriteList.on_update` on the scene's sprite lists.

        By default, this method calls :py:meth:`~arcade.SpriteList.on_update`
        on the scene's sprite lists in the default draw order.

        You can limit and reorder the updates with the ``names``
        argument by passing a list of names in the scene. The sprite
        lists will be drawn in the order of the passed iterable. If a
        name is not in the scene, a :py:class:`KeyError` will be raised.

        :param delta_time: The time step to update by in seconds.
        :param names: Which layers & what order to update them in.
        """
        if names:
            for name in names:
                self._name_mapping[name].on_update(delta_time)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.on_update(delta_time)

    def update_animation(
        self, delta_time: float, names: Optional[Iterable[str]] = None
    ) -> None:
        """
        Call :py:meth:`~arcade.SpriteList.update_animation` on the scene's sprite lists.

        By default, this method calls :py:meth:`~arcade.SpriteList.update_animation`
        on each sprite list in the scene in the default draw order.

        You can limit and reorder the updates with the ``names``
        argument by passing a list of names in the scene. The sprite
        lists will be drawn in the order of the passed iterable. If a
        name is not in the scene, a :py:class:`KeyError` will be raised.

        :param delta_time: The time step to update by in seconds.
        :param names: Which layers & what order to update them in.
        """
        if names:
            for name in names:
                self._name_mapping[name].update_animation(delta_time)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.update_animation(delta_time)

    def draw(
        self,
        names: Optional[Iterable[str]] = None,
        filter: Optional[int] = None,
        pixelated: bool = False,
        blend_function: Optional[Union[Tuple[int, int], Tuple[int, int, int, int]]] = None,
        **kwargs
    ) -> None:
        """
        Call :py:meth:`~arcade.SpriteList.draw` on the scene's sprite lists.

        By default, this method calls :py:meth:`~arcade.SpriteList.draw`
        on each sprite list in the scene in the default draw order.

        You can limit and reorder the draw calls with the ``names``
        argument by passing a list of names in the scene. The sprite
        lists will be drawn in the order of the passed iterable. If a
        name is not in the scene, a :py:class:`KeyError` will be raised.

        The other named keyword arguments are the same as those of
        :py:meth:`SpriteList.draw() <arcade.SpriteList.draw>`. The
        ``**kwargs`` option is for advanced users who have
        subclassed :py:class:`~arcade.SpriteList`.

        :param names: Which layers to draw & what order to draw them in.
        :param filter: Optional parameter to set OpenGL filter, such as
           ``gl.GL_NEAREST`` to avoid smoothing.
        :param pixelated: ``True`` for pixel art and ``False`` for
            smooth scaling.
        :param blend_function:
            Use the specified OpenGL blend function while drawing the
            sprite list, such as ``arcade.Window.ctx.BLEND_ADDITIVE``
            or ``arcade.Window.ctx.BLEND_DEFAULT``.
        """

        if names:
            for name in names:
                self._name_mapping[name].draw(
                    filter=filter,
                    pixelated=pixelated,
                    blend_function=blend_function,
                    **kwargs
                )
            return

        for sprite_list in self._sprite_lists:
            sprite_list.draw(
                filter=filter,
                pixelated=pixelated,
                blend_function=blend_function,
                **kwargs
            )

    def draw_hit_boxes(
        self,
        color: RGBA255 = Color(0, 0, 0, 255),
        line_thickness: float = 1.0,
        names: Optional[Iterable[str]] = None,
    ) -> None:
        """
        Draw debug hit box outlines for sprites in the scene's layers.

        If ``names`` is a valid iterable of layer names in the scene, then hit boxes
        will be drawn for the specified layers in the order of the passed iterable.

        If `names` is not provided, then every layer's hit boxes will be drawn in the
        order specified.

        :param color: The RGBA color to use to draw the hit boxes with.
        :param line_thickness: How many pixels thick the hit box outlines should be
        :param names: Which layers & what order to draw their hit boxes in.
        """

        if names:
            for name in names:
                self._name_mapping[name].draw_hit_boxes(color, line_thickness)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.draw_hit_boxes(color, line_thickness)

    def __bool__(self) -> bool:
        """Returns whether or not `_sprite_lists` contains anything"""
        return bool(self._sprite_lists)

    def __contains__(self, item: Union[str, SpriteList]) -> bool:
        """True when `item` is in `_sprite_lists` or is a value in `_name_mapping`"""
        return item in self._sprite_lists or item in self._name_mapping
