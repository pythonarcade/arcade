from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

    from .context import Context

_current_provider: BaseProvider = None


def set_provider(provider_name: str):
    global _current_provider

    try:
        module = importlib.import_module(f"arcade.gl.backends.{provider_name}.provider")
        _current_provider = module.Provider()
    except ImportError as e:
        print(e)
        raise ImportError(f"arcade.gl Backend Provider '{provider_name}' not found")


def get_provider():
    return _current_provider


def get_context(*args, **kwargs) -> Context:
    if _current_provider is None:
        set_provider("gl")

    return _current_provider.create_context(*args, **kwargs)


def get_arcade_context(*args, **kwargs) -> ArcadeContext:
    if _current_provider is None:
        set_provider("gl")

    return _current_provider.create_arcade_context(*args, **kwargs)


class BaseProvider(ABC):
    @abstractmethod
    def create_context(self, *args, **kwargs) -> Context:
        pass

    @abstractmethod
    def create_info(self, ctx: Context):
        pass

    @abstractmethod
    def create_arcade_context(self, *args, **kwargs) -> ArcadeContext:
        pass
