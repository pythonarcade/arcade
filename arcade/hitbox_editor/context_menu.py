"""Right-click context menu for the HitBox Editor."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

import arcade
from arcade.gui import UIManager
from arcade.gui.widgets import UIWidget
from arcade.gui.widgets.buttons import UIFlatButton
from arcade.gui.widgets.layout import UIBoxLayout
from arcade.types import Color

if TYPE_CHECKING:
    from arcade.hitbox_editor.state import EditorState


class ContextMenuItem(UIFlatButton):
    """A single item in the context menu."""

    def __init__(
        self,
        text: str,
        callback: Callable[[], None],
        enabled: bool = True,
        width: float = 200,
        height: float = 28,
    ) -> None:
        super().__init__(text=text, width=width, height=height)
        self._callback = callback
        self._enabled = enabled
        if not enabled:
            self.disabled = True

    def on_click(self, event) -> None:
        if self._enabled:
            self._callback()


class ContextMenuSeparator(UIWidget):
    """A visual separator line in the context menu."""

    def __init__(self, width: float = 200) -> None:
        super().__init__(width=width, height=6)

    def do_render(self, surface) -> None:
        self.prepare_render(surface)
        arcade.draw_line(
            4, self.content_height / 2,
            self.content_width - 4, self.content_height / 2,
            (100, 100, 100, 180), 1,
        )


class ContextMenu(UIBoxLayout):
    """A right-click context menu shown as an overlay."""

    def __init__(
        self,
        state: EditorState,
        ui_manager: UIManager,
        x: float,
        y: float,
        on_dismiss: Callable[[], None],
        world_x: float = 0.0,
        world_y: float = 0.0,
    ) -> None:
        super().__init__(vertical=True, space_between=1)
        self._state = state
        self._ui_manager = ui_manager
        self._on_dismiss = on_dismiss
        self._world_x = world_x
        self._world_y = world_y

        self._build_items()

        # Position at click location
        self.rect = self.rect.move(x, y)

    def _build_items(self) -> None:
        """Build context menu items based on current state."""
        state = self._state
        has_selection = len(state.selected_points) > 0
        has_clipboard = state.clipboard is not None and state.clipboard.has_content()
        has_active = state.active_region is not None
        can_undo = state.history is not None and state.history.can_undo()
        can_redo = state.history is not None and state.history.can_redo()

        # Add point here
        self.add(ContextMenuItem(
            "Add Point Here",
            self._add_point_here,
            enabled=has_active,
        ))

        self.add(ContextMenuSeparator())

        # Edit operations
        self.add(ContextMenuItem("Cut        Ctrl+X", self._cut, enabled=has_selection))
        self.add(ContextMenuItem("Copy       Ctrl+C", self._copy, enabled=has_selection))
        self.add(ContextMenuItem("Paste      Ctrl+V", self._paste, enabled=has_clipboard and has_active))

        self.add(ContextMenuSeparator())

        # Undo/Redo
        self.add(ContextMenuItem("Undo       Ctrl+Z", self._undo, enabled=can_undo))
        self.add(ContextMenuItem("Redo  Ctrl+Shift+Z", self._redo, enabled=can_redo))

        self.add(ContextMenuSeparator())

        # Selection
        self.add(ContextMenuItem("Select All   Ctrl+A", self._select_all, enabled=has_active))
        self.add(ContextMenuItem("Delete Selected", self._delete_selected, enabled=has_selection))

    def _dismiss(self) -> None:
        self._on_dismiss()

    def _add_point_here(self) -> None:
        from arcade.hitbox_editor.history import AddPointCommand

        state = self._state
        if state.active_region is not None and state.history is not None:
            points = state.regions.get(state.active_region, [])
            cmd = AddPointCommand(
                state.active_region, len(points), (self._world_x, self._world_y)
            )
            state.history.execute(cmd, state)
        self._dismiss()

    def _cut(self) -> None:
        if self._state.clipboard:
            self._state.clipboard.cut(self._state)
        self._dismiss()

    def _copy(self) -> None:
        if self._state.clipboard:
            self._state.clipboard.copy(self._state)
        self._dismiss()

    def _paste(self) -> None:
        if self._state.clipboard:
            self._state.clipboard.paste(self._state)
        self._dismiss()

    def _undo(self) -> None:
        if self._state.history:
            self._state.history.undo(self._state)
        self._dismiss()

    def _redo(self) -> None:
        if self._state.history:
            self._state.history.redo(self._state)
        self._dismiss()

    def _select_all(self) -> None:
        state = self._state
        if state.active_region and state.active_region in state.regions:
            state.selected_points.clear()
            for i in range(len(state.regions[state.active_region])):
                state.selected_points.add((state.active_region, i))
        self._dismiss()

    def _delete_selected(self) -> None:
        from arcade.hitbox_editor.history import CompositeCommand, RemovePointCommand

        state = self._state
        if not state.selected_points or state.history is None:
            self._dismiss()
            return

        removals = []
        for region_name, index in sorted(state.selected_points, reverse=True):
            if region_name in state.regions and index < len(state.regions[region_name]):
                point = state.regions[region_name][index]
                removals.append(RemovePointCommand(region_name, index, point))

        if removals:
            cmd = CompositeCommand(removals, "Delete selected points")
            state.history.execute(cmd, state)
            state.selected_points.clear()

        self._dismiss()
