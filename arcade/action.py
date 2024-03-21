from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from typing_extensions import TypedDict

import arcade
from arcade.resources import resolve

RawAction = TypedDict(
    "RawAction",
    {
        "name": str,
        "keys": List[int]
    }
)

RawActionMapping = TypedDict(
    "RawActionMapping",
    {
        "actions": List[RawAction],
    }
)


class ActionState(Enum):
    PRESSED = 1,
    RELEASED = 0


class Action:
    def __init__(self, keys: Set[int]):
        self._keys: Set[int] = keys

    @property
    def keys(self) -> Set[int]:
        return self._keys

    @keys.setter
    def keys(self, value: Set[int]) -> None:
        self._keys = value

    def add_key(self, key: int):
        self._keys.add(key)

    def remove_key(self, key: int) -> None:
        try:
            self._keys.remove(key)
        except KeyError:
            pass

class ActionManager:
    
    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self.action_subscribers: Dict[str, Set[Callable[[ActionState, int], Any]]] = {}
        self.keys_to_actions: Dict[int, Set[str]] = {}

        for key in [key for key in dir(arcade.key) if not key.startswith('__')]:
            self.keys_to_actions[getattr(arcade.key, key)] = set()

        window = arcade.get_window()
        window.push_handlers(
            self.on_key_press,
            self.on_key_release,
        )

    @classmethod
    def from_json(cls, raw_mapping: RawActionMapping) -> ActionManager:
        manager = cls()

        for raw_action in raw_mapping["actions"]:
            manager.register_action(raw_action["name"], raw_action["keys"])

        return manager

    @classmethod
    def from_json_string(cls, raw_json: str) -> ActionManager:
        return ActionManager.from_json(json.loads(raw_json))

    @classmethod
    def from_json_file(cls, file: Union[str, Path]) -> ActionManager:
        file = resolve(file)
        with open(file) as mapping_file:
            return ActionManager.from_json(json.load(mapping_file))

    def register_action(self, name: str, keys: List[int] = []):
        if name in self.actions:
            raise AttributeError("Tried to create a duplicate action")
    
        action = Action(set(keys))
        self.actions[name] = action
        
        for key in action.keys:
            self.keys_to_actions[key].add(name)

    def remove_action(self, name: str):
        keys = self.actions[name].keys
        for key in keys:
            key_list = self.keys_to_actions[key]
            key_list.remove(name)

        if name in self.action_subscribers:
            del self.action_subscribers[name]

        if name in self.actions:
            del self.actions[name]

    def register_input(self, name: str, keys: List[int] = []):
        for key in keys:
            self.actions[name].add_key(key)
            self.keys_to_actions[key].add(name)

    def remove_input(self, name: str, keys: List[int] = []):
        for key in keys:
            self.actions[name].remove_key(key)

    def subscribe_to_action(self, name: str, subscriber: Callable[[ActionState, int], Any]):
        old = self.action_subscribers.get(name, set())
        old.add(subscriber)
        self.action_subscribers[name] = old

    def on_key_press(self, key: int, modifiers) -> None:
        if self.action_subscribers:
            window = arcade.get_window()
            for action in self.keys_to_actions[key]:
                window.dispatch_event("on_action", action, ActionState.PRESSED, key)
                for subscriber in tuple(self.action_subscribers.get(action, set())):
                    subscriber(ActionState.PRESSED, key)

    def on_key_release(self, key: int, modifiers) -> None:
        if self.action_subscribers:
            window = arcade.get_window()
            for action in self.keys_to_actions[key]:
                window.dispatch_event("on_action", action, ActionState.RELEASED, key)
                for subscriber in tuple(self.action_subscribers.get(action, set())):
                    subscriber(ActionState.RELEASED, key)

