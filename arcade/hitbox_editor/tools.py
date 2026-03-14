"""Tool implementations for the HitBox Editor."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from arcade.hitbox_editor.history import (
    AddPointCommand,
    MoveMultiplePointsCommand,
    MovePointCommand,
    RemovePointCommand,
)

if TYPE_CHECKING:
    from arcade.hitbox_editor.state import EditorState

# Mouse buttons
MOUSE_LEFT = 1
MOUSE_RIGHT = 4
MOUSE_MIDDLE = 2

# Modifier keys
MOD_SHIFT = 1


class BaseTool(ABC):
    """Base class for editor tools."""

    @abstractmethod
    def on_press(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        ...

    @abstractmethod
    def on_drag(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        dx: float,
        dy: float,
    ) -> None:
        ...

    @abstractmethod
    def on_release(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        ...


class AddTool(BaseTool):
    """Tool for adding points to the active region."""

    def on_press(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        if button != MOUSE_LEFT:
            return
        if state.active_region is None or state.history is None:
            return
        if state.active_region not in state.regions:
            return

        point = (wx, wy)
        points = state.regions[state.active_region]

        # Check if click is near an existing edge - if so, insert there
        if len(points) >= 2:
            edge = state.find_nearest_edge(wx, wy, threshold=state.pick_threshold)
            if edge is not None and edge[0] == state.active_region:
                cmd = AddPointCommand(state.active_region, edge[1], point)
                state.history.execute(cmd, state)
                return

        # Otherwise append to end
        cmd = AddPointCommand(state.active_region, len(points), point)
        state.history.execute(cmd, state)

    def on_drag(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        dx: float,
        dy: float,
    ) -> None:
        pass

    def on_release(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        pass


class SelectTool(BaseTool):
    """Tool for selecting and moving points.

    Supports click-to-select, shift+click multi-select, drag-to-move,
    and drag-on-empty-space to draw a selection rectangle.
    """

    def __init__(self) -> None:
        # Track drag state for move command batching
        self._dragging = False
        self._drag_start_positions: dict[tuple[str, int], tuple[float, float]] = {}
        # Track drag-to-select rectangle state
        self._rect_selecting = False
        self._rect_start: tuple[float, float] = (0.0, 0.0)
        self._shift_held = False

    def on_press(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        if button != MOUSE_LEFT:
            return

        self._shift_held = bool(modifiers & MOD_SHIFT)
        nearest = state.find_nearest_point(wx, wy, threshold=state.pick_threshold)

        if nearest is None:
            # Click on empty space — start a selection rectangle
            if not self._shift_held:
                state.selected_points.clear()
            self._rect_selecting = True
            self._rect_start = (wx, wy)
            state.selection_rect = (wx, wy, wx, wy)
            return

        region_name, index = nearest

        if self._shift_held:
            # Toggle point in selection
            key = (region_name, index)
            if key in state.selected_points:
                state.selected_points.discard(key)
            else:
                state.selected_points.add(key)
        else:
            # If clicking on an already-selected point, keep multi-select for drag
            key = (region_name, index)
            if key not in state.selected_points:
                state.selected_points.clear()
                state.selected_points.add(key)

        # Set active region to match clicked point
        state.active_region = region_name

        # Record start positions for drag-to-move
        if state.selected_points:
            self._dragging = True
            self._drag_start_positions = {}
            for r, i in state.selected_points:
                if r in state.regions and i < len(state.regions[r]):
                    self._drag_start_positions[(r, i)] = state.regions[r][i]

    def on_drag(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        dx: float,
        dy: float,
    ) -> None:
        # Selection rectangle drag
        if self._rect_selecting:
            sx, sy = self._rect_start
            state.selection_rect = (sx, sy, wx, wy)
            return

        # Point move drag
        if not self._dragging or not state.selected_points:
            return

        for r, i in state.selected_points:
            if r in state.regions and i < len(state.regions[r]):
                old_x, old_y = state.regions[r][i]
                state.regions[r][i] = (old_x + dx, old_y + dy)

    def on_release(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        if button != MOUSE_LEFT:
            return

        # Finish selection rectangle
        if self._rect_selecting:
            sx, sy = self._rect_start
            selected = state.find_points_in_rect(sx, sy, wx, wy)
            if self._shift_held:
                state.selected_points |= selected
            else:
                state.selected_points = selected
            state.selection_rect = None
            self._rect_selecting = False
            return

        # Finish point move
        if not self._dragging or state.history is None:
            self._dragging = False
            return

        moves: list[tuple[str, int, tuple[float, float], tuple[float, float]]] = []
        for (r, i), old_pos in self._drag_start_positions.items():
            if r in state.regions and i < len(state.regions[r]):
                new_pos = state.regions[r][i]
                if old_pos != new_pos:
                    moves.append((r, i, old_pos, new_pos))

        if moves:
            if len(moves) == 1:
                r, i, old_pos, new_pos = moves[0]
                cmd = MovePointCommand(r, i, old_pos, new_pos)
            else:
                cmd = MoveMultiplePointsCommand(moves)
            # Don't re-execute - points are already moved. Push directly to undo stack.
            state.history._undo_stack.append(cmd)
            if len(state.history._undo_stack) > state.history.max_history:
                state.history._undo_stack.pop(0)
            state.history._redo_stack.clear()

        self._dragging = False
        self._drag_start_positions.clear()


class DeleteTool(BaseTool):
    """Tool for deleting points."""

    def on_press(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        if button != MOUSE_LEFT:
            return
        if state.history is None:
            return

        nearest = state.find_nearest_point(wx, wy, threshold=state.pick_threshold)
        if nearest is None:
            return

        region_name, index = nearest
        point = state.regions[region_name][index]
        cmd = RemovePointCommand(region_name, index, point)
        state.history.execute(cmd, state)

    def on_drag(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        dx: float,
        dy: float,
    ) -> None:
        pass

    def on_release(
        self,
        state: EditorState,
        wx: float,
        wy: float,
        button: int,
        modifiers: int,
    ) -> None:
        pass
