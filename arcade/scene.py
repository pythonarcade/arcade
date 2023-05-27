"""
This module provides a Scene Manager class.

This class let's you add Sprites/SpriteLists to a scene and give them
a name, as well as control the draw order. In addition it provides a
helper function to create a Scene directly from a TileMap object.
"""

from typing import Dict, List, Optional, Union

from arcade import Sprite, SpriteList
from arcade.types import Color, RGBA255
from arcade.tilemap import TileMap

from warnings import warn

__all__ = ["Scene"]


class Scene:
    """
    Uses :py:class:`~arcade.SpriteList` instances as layers, allowing bulk updates & drawing.

    The primary use of this class is to update or draw multiple sprite lists
    with single calls. It also provides convenience methods, but some of them
    trade execution speed for convenience.

    * Fine-grained convenience methods for adding, deleting, and reordering
      sprite lists
    * :py:meth:`.from_tilemap`, which creates a new scene from a
      :py:class:`~arcade.tilemap.TileMap` already loaded from tiled data
    * Flexible but slow convenience methods & support for python keywords such
      as ``in``, ``del``

    For an example of how to use this class, see :ref:`platformer_part_three`.
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

                 This method uses :py:func:`isinstance`, which can be slow.

        Consider the following alternatives:

        * :py:meth:`.remove_sprite_list_by_index`
        * :py:meth:`.remove_sprite_list_by_name`
        * :py:meth:`.remove_sprite_list_by_object`

        :param Union[int, str, SpriteList] sprite_list:
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
        Create a new Scene from a `TileMap` object.

        The SpriteLists will use the layer names and ordering as defined in the
        Tiled file.

        :param TileMap tilemap: The `TileMap` object to create the scene from.
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
        * directly accessing ``scene_instance._name_mapping``, although this may
          get flagged by linters as bad style.

        :param str name: The name of the `SpriteList` to retrieve.
        """
        return self._name_mapping[name]

    def __getitem__(self, key: str) -> SpriteList:
        """
        Retrieve a `SpriteList` by name.

        This is here for ease of use to make sub-scripting the scene object directly
        to retrieve a SpriteList possible.

        :param str key: The name of the 'SpriteList' to retreive.
        """
        if key in self._name_mapping:
            return self._name_mapping[key]

        raise KeyError(f"Scene does not contain a layer named: {key}")

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

        :param str name: The name of the `SpriteList` to add to or create.
        :param Sprite sprite: The `Sprite` to add.
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

        This will add a new SpriteList to the scene at the end of the draw order.

        If no SpriteList is supplied via the `sprite_list` parameter then a new one will be
        created, and the `use_spatial_hash` parameter will be respected for that creation.

        :param str name: The name to give the SpriteList.
        :param bool use_spatial_hash: Wether or not to use spatial hash if creating a new SpriteList.
        :param SpriteList sprite_list: The SpriteList to add, optional.
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
        Add a SpriteList to the scene with the specified name before a specific SpriteList.

        This will add a new SpriteList to the scene before the specified SpriteList in the draw order.

        If no SpriteList is supplied via the `sprite_list` parameter then a new one will be
        created, and the `use_spatial_hash` parameter will be respected for that creation.

        :param str name: The name to give the SpriteList.
        :param str before: The name of the SpriteList to place this one before.
        :param bool use_spatial_hash: Wether or not to use spatial hash if creating a new SpriteList.
        :param SpriteList sprite_list: The SpriteList to add, optional.
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
        Move a given SpriteList in the scene to before another given SpriteList.

        This will adjust the render order so that the SpriteList specified by `name`
        is placed before the one specified by `before`.

        :param str name: The name of the SpriteList to move.
        :param str before: The name of the SpriteList to place it before.
        """
        if name not in self._name_mapping:
            raise ValueError(
                f"Tried to move unknown SpriteList with the name {name} in Scene"
            )

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

        This will add a new SpriteList to the scene after the specified SpriteList in the draw order.
        If no SpriteList is supplied via the `sprite_list` parameter then a new one will be
        created, and the `use_spatial_hash` parameter will be respected for that creation.

        :param str name: The name to give the SpriteList.
        :param str after: The name of the SpriteList to place this one after.
        :param bool use_spatial_hash: Whether or not to use spatial hash if creating a new SpriteList.
        :param SpriteList sprite_list: The SpriteList to add, optional.
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
        Move a given SpriteList in the scene to be after another given SpriteList.

        This will adjust the render order so that the SpriteList specified by `name`
        is placed after the one specified by `after`.

        :param str name: The name of the SpriteList to move.
        :param str after: The name of the SpriteList to place it after.
        """
        if name not in self._name_mapping:
            raise ValueError(
                f"Tried to move unknown SpriteList with the name {name} in Scene"
            )

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
        Remove a SpriteList from the scene by its index in the draw order.

        :param int index: The index of the SpriteList to remove.
        """
        self.remove_sprite_list_by_object(self._sprite_lists[index])

    def remove_sprite_list_by_name(
        self,
        name: str,
    ) -> None:
        """
        Remove a SpriteList from the scene by its name.

        A :py:class:`KeyError` will be raised if the SpriteList is not
        in the scene.

        :param str name: The name of the SpriteList to remove.
        """
        sprite_list = self._name_mapping[name]
        self._sprite_lists.remove(sprite_list)
        del self._name_mapping[name]

    def remove_sprite_list_by_object(self, sprite_list: SpriteList) -> None:
        """
        Remove the passed SpriteList instance from the Scene.

        A :py:class:`ValueError` will be raised if the passed sprite
        list is not in the scene.

        :param SpriteList sprite_list: The SpriteList to remove.
        """
        self._sprite_lists.remove(sprite_list)
        self._name_mapping = {
            key: val for key, val in self._name_mapping.items() if val != sprite_list
        }

    def update(self, names: Optional[List[str]] = None) -> None:
        """
        Used to update SpriteLists contained in the scene.

        If `names` parameter is provided then only the specified spritelists
        will be updated. If `names` is not provided, then every SpriteList
        in the scene will be updated.

        :param Optional[List[str]] names: A list of names of SpriteLists to update.
        """
        if names:
            for name in names:
                self._name_mapping[name].update()
            return

        for sprite_list in self._sprite_lists:
            sprite_list.update()

    def on_update(self, delta_time: float = 1 / 60, names: Optional[List[str]] = None) -> None:
        """
        Used to call on_update of SpriteLists contained in the scene.

        Similar to update() but allows passing a delta_time variable.
        If `names` parameter is provided then only the specified spritelists
        will be updated. If `names` is not provided, then every SpriteList
        in the scene will have on_update called.

        :param float delta_time: Time since last update.
        :param Optional[List[str]] names: A list of names of SpriteLists to update.
        """
        if names:
            for name in names:
                self._name_mapping[name].on_update(delta_time)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.on_update(delta_time)

    def update_animation(
        self, delta_time: float, names: Optional[List[str]] = None
    ) -> None:
        """
        Used to update the animation of SpriteLists contained in the scene.

        If `names` parameter is provided then only the specified spritelists
        will be updated. If `names` is not provided, then every SpriteList
        in the scene will be updated.

        :param float delta_time: The delta time for the update.
        :param Optional[List[str]] names: A list of names of SpriteLists to update.
        """
        if names:
            for name in names:
                self._name_mapping[name].update_animation(delta_time)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.update_animation(delta_time)

    def draw(self, names: Optional[List[str]] = None, **kwargs) -> None:
        """
        Draw the Scene.

        If `names` parameter is provided then only the specified SpriteLists
        will be drawn. They will be drawn in the order that the names in the
        list were arranged. If `names` is not provided, then every SpriteList
        in the scene will be drawn according the order of the main _sprite_lists
        attribute of the Scene.

        :param Optional[List[str]] names: A list of names of SpriteLists to draw.
        :param filter: Optional parameter to set OpenGL filter, such as
                       `gl.GL_NEAREST` to avoid smoothing.
        :param blend_function: Optional parameter to set the OpenGL blend function
            used for drawing the sprite list, such as `arcade.Window.ctx.BLEND_ADDITIVE`
            or `arcade.Window.ctx.BLEND_DEFAULT`
        """

        if names:
            for name in names:
                self._name_mapping[name].draw(**kwargs)
            return

        for sprite_list in self._sprite_lists:
            sprite_list.draw(**kwargs)

    def draw_hit_boxes(
        self,
        color: RGBA255 = Color(0, 0, 0, 255),
        line_thickness: float = 1,
        names: Optional[List[str]] = None,
    ) -> None:
        """
        Draw hitboxes for all sprites in the scene.

        If `names` parameter is provided then only the specified SpriteLists
        will be drawn. They will be drawn in the order that the names in the
        list were arranged. If `names` is not provided, then every SpriteList
        in the scene will be drawn according to the order of the main _sprite_lists
        attribute of the Scene.
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
