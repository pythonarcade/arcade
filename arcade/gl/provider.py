from __future__ import annotations

import importlib
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

    from .context import Context, Info

_current_provider: Optional[BaseProvider] = None


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
        set_provider("opengl")

    assert _current_provider is not None  # this can't really be None at this point, but mypy

    return _current_provider.create_context(*args, **kwargs)


def get_arcade_context(*args, **kwargs) -> ArcadeContext:
    if _current_provider is None:
        set_provider("opengl")

    assert _current_provider is not None  # this can't really be None at this point, but mypy

    return _current_provider.create_arcade_context(*args, **kwargs)


class BaseProvider(ABC):
    @abstractmethod
    def create_context(self, *args, **kwargs) -> Context:
        pass

    @abstractmethod
    def create_info(self, ctx: Context) -> Info:
        pass

    @abstractmethod
    def create_arcade_context(self, *args, **kwargs) -> ArcadeContext:
        pass
