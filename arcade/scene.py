from typing import Dict, List, Optional, Union

from arcade import SpriteList
from arcade.tilemap import TileMap


class Scene:
    def __init__(self) -> None:
        self.sprite_lists: List[SpriteList] = []
        self.name_mapping: Dict[str, SpriteList] = {}

    @classmethod
    def from_tilemap(cls, tilemap: TileMap) -> "Scene":
        scene = cls()
        for name, sprite_list in tilemap.sprite_lists.items():
            scene.add_sprite_list(name, sprite_list)
        return scene

    def get_sprite_list(self, name: str) -> SpriteList:
        return self.name_mapping[name]

    def add_sprite_list(
        self,
        name: str,
        sprite_list: SpriteList,
    ) -> None:
        self.name_mapping[name] = sprite_list
        self.sprite_lists.append(sprite_list)

    def add_sprite_list_before(
        self, name: str, sprite_list: SpriteList, before: str
    ) -> None:
        self.name_mapping[name] = sprite_list
        before_list = self.name_mapping[before]
        index = self.sprite_lists.index(before_list) - 1
        self.sprite_lists.insert(index, sprite_list)

    def add_sprite_list_after(
        self, name: str, sprite_list: SpriteList, after: str
    ) -> None:
        self.name_mapping[name] = sprite_list
        after_list = self.name_mapping[after]
        index = self.sprite_lists.index(after_list)
        self.sprite_lists.insert(index, sprite_list)

    def remove_sprite_list_by_name(
        self,
        name: str,
    ) -> None:
        sprite_list = self.name_mapping[name]
        self.sprite_lists.remove(sprite_list)
        del self.name_mapping[name]

    def remove_sprite_list_by_object(self, sprite_list: SpriteList) -> None:
        self.sprite_lists.remove(sprite_list)
        self.name_mapping = {
            key: val for key, val in self.name_mapping.items() if val != sprite_list
        }

    def update(self, names: Optional[Union[str, List[str]]] = None) -> None:
        """
        Used to update SpriteLists contained in the scene.

        If `names` parameter is provided then only the specified spritelists
        will be updated. A single name or a list of names can be passed to the
        parameter. If `names` is not provided, then every sprite_list in the scene
        will be updated.

        :param Union[str, List[str]] names: A name or list of names of SpriteLists to update
        """
        if names:
            if isinstance(names, str):
                self.name_mapping[names].update()
            elif isinstance(names, list):
                for name in names:
                    self.name_mapping[name].update()
            return

        for sprite_list in self.sprite_lists:
            sprite_list.update()

    def update_animation(
        self, delta_time: float, names: Optional[Union[str, List[str]]] = None
    ) -> None:
        """
        Used to update the animation of SpriteLists contained in the scene.

        If `names` parameter is provided then only the specified spritelists
        will be updated. A single name or a list of names can be passed to the
        parameter. If `names` is not provided, then every sprite_list in the scene
        will be updated.

        :param float delta_time: The delta time for the update.
        :param Union[str, List[str]] names: A name or list of names of SpriteLists to update.
        """
        if names:
            if isinstance(names, str):
                self.name_mapping[names].update_animation(delta_time)
            elif isinstance(names, list):
                for name in names:
                    self.name_mapping[name].update_animation(delta_time)
            return

        for sprite_list in self.sprite_lists:
            sprite_list.update_animation(delta_time)

    def draw(self) -> None:
        for sprite_list in self.sprite_lists:
            sprite_list.draw()
