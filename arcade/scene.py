from typing import Dict, List, Optional

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

    def draw(self) -> None:
        for sprite_list in self.sprite_lists:
            sprite_list.draw()
