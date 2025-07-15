from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.math import Mat4
from arcade.types import LBWH

from .viewport import ViewportProjector

if TYPE_CHECKING:
    from arcade.context import ArcadeContext

__all__ = ("DefaultProjector",)


class DefaultProjector(ViewportProjector):
    """
    An extremely limited projector which lacks any kind of control. This is only
    here to act as the default camera used internally by Arcade. There should be
    no instance where a developer would want to use this class.

    Args:
        context: The window context to bind the camera to. Defaults to the currently active window.
    """

    def __init__(self, *, context: ArcadeContext | None = None):
        super().__init__(context=context)

    def use(self) -> None:
        """
        Set the window's Projection and View matrices.

        cache's the window viewport to determine the projection matrix.
        """

        viewport = self.viewport.lbwh_int
        # If the viewport is correct and the default camera is in use,
        # then don't waste time resetting the view and projection matrices
        if self._ctx.viewport == viewport and self._ctx.current_camera == self:
            return

        # If the viewport has changed while the default camera is active then the
        # default needs to update itself.
        # If it was another camera's viewport being used the default camera should not update.
        if self._ctx.viewport != viewport and self._ctx.current_camera == self:
            self.viewport = LBWH(*self._ctx.viewport)
        else:
            self._ctx.viewport = viewport

        self._ctx.current_camera = self

        self._ctx.view_matrix = Mat4()
        self._ctx.projection_matrix = self._projection_matrix
