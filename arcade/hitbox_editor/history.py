"""Undo/redo command pattern and clipboard for the HitBox Editor."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arcade.hitbox_editor.state import EditorState


class Command(ABC):
    """Base class for undoable editor commands."""

    @abstractmethod
    def execute(self, state: EditorState) -> None:
        ...

    @abstractmethod
    def undo(self, state: EditorState) -> None:
        ...

    @abstractmethod
    def description(self) -> str:
        ...


class CommandHistory:
    """Manages undo/redo stacks of commands."""

    def __init__(self, max_history: int = 100) -> None:
        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []
        self.max_history = max_history

    def execute(self, command: Command, state: EditorState) -> None:
        """Execute a command and push it onto the undo stack."""
        command.execute(state)
        self._undo_stack.append(command)
        if len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)
        self._redo_stack.clear()

    def undo(self, state: EditorState) -> None:
        """Undo the last command."""
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo(state)
        self._redo_stack.append(command)

    def redo(self, state: EditorState) -> None:
        """Redo the last undone command."""
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.execute(state)
        self._undo_stack.append(command)

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0


# --- Command implementations ---


class AddPointCommand(Command):
    """Add a point to a region at a given index."""

    def __init__(self, region: str, index: int, point: tuple[float, float]) -> None:
        self.region = region
        self.index = index
        self.point = point

    def execute(self, state: EditorState) -> None:
        state.regions[self.region].insert(self.index, self.point)

    def undo(self, state: EditorState) -> None:
        state.regions[self.region].pop(self.index)

    def description(self) -> str:
        return "Add point"


class RemovePointCommand(Command):
    """Remove a point from a region at a given index."""

    def __init__(self, region: str, index: int, point: tuple[float, float]) -> None:
        self.region = region
        self.index = index
        self.point = point

    def execute(self, state: EditorState) -> None:
        state.regions[self.region].pop(self.index)
        # Clean up selection
        state.selected_points.discard((self.region, self.index))

    def undo(self, state: EditorState) -> None:
        state.regions[self.region].insert(self.index, self.point)

    def description(self) -> str:
        return "Remove point"


class MovePointCommand(Command):
    """Move a point from old_pos to new_pos."""

    def __init__(
        self,
        region: str,
        index: int,
        old_pos: tuple[float, float],
        new_pos: tuple[float, float],
    ) -> None:
        self.region = region
        self.index = index
        self.old_pos = old_pos
        self.new_pos = new_pos

    def execute(self, state: EditorState) -> None:
        state.regions[self.region][self.index] = self.new_pos

    def undo(self, state: EditorState) -> None:
        state.regions[self.region][self.index] = self.old_pos

    def description(self) -> str:
        return "Move point"


class MoveMultiplePointsCommand(Command):
    """Move multiple points by a delta."""

    def __init__(
        self,
        moves: list[tuple[str, int, tuple[float, float], tuple[float, float]]],
    ) -> None:
        # Each entry: (region, index, old_pos, new_pos)
        self.moves = moves

    def execute(self, state: EditorState) -> None:
        for region, index, _, new_pos in self.moves:
            state.regions[region][index] = new_pos

    def undo(self, state: EditorState) -> None:
        for region, index, old_pos, _ in self.moves:
            state.regions[region][index] = old_pos

    def description(self) -> str:
        return f"Move {len(self.moves)} points"


class AddRegionCommand(Command):
    """Add a new empty region."""

    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, state: EditorState) -> None:
        state.regions[self.name] = []
        state.active_region = self.name

    def undo(self, state: EditorState) -> None:
        del state.regions[self.name]
        if state.active_region == self.name:
            state.active_region = next(iter(state.regions), None)

    def description(self) -> str:
        return f"Add region '{self.name}'"


class RemoveRegionCommand(Command):
    """Remove a region, saving its points for undo."""

    def __init__(self, name: str, points: list[tuple[float, float]]) -> None:
        self.name = name
        self.points = points

    def execute(self, state: EditorState) -> None:
        del state.regions[self.name]
        # Remove any selected points in this region
        state.selected_points = {
            (r, i) for r, i in state.selected_points if r != self.name
        }
        if state.active_region == self.name:
            state.active_region = next(iter(state.regions), None)

    def undo(self, state: EditorState) -> None:
        state.regions[self.name] = list(self.points)
        state.active_region = self.name

    def description(self) -> str:
        return f"Remove region '{self.name}'"


class RenameRegionCommand(Command):
    """Rename a region."""

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name

    def execute(self, state: EditorState) -> None:
        state.regions[self.new_name] = state.regions.pop(self.old_name)
        # Update selection references
        state.selected_points = {
            (self.new_name if r == self.old_name else r, i)
            for r, i in state.selected_points
        }
        if state.active_region == self.old_name:
            state.active_region = self.new_name

    def undo(self, state: EditorState) -> None:
        state.regions[self.old_name] = state.regions.pop(self.new_name)
        state.selected_points = {
            (self.old_name if r == self.new_name else r, i)
            for r, i in state.selected_points
        }
        if state.active_region == self.new_name:
            state.active_region = self.old_name

    def description(self) -> str:
        return f"Rename region '{self.old_name}' to '{self.new_name}'"


class PastePointsCommand(Command):
    """Insert multiple points into a region."""

    def __init__(
        self, region: str, index: int, points: list[tuple[float, float]]
    ) -> None:
        self.region = region
        self.index = index
        self.points = points

    def execute(self, state: EditorState) -> None:
        for i, pt in enumerate(self.points):
            state.regions[self.region].insert(self.index + i, pt)

    def undo(self, state: EditorState) -> None:
        for _ in self.points:
            state.regions[self.region].pop(self.index)

    def description(self) -> str:
        return f"Paste {len(self.points)} points"


class CompositeCommand(Command):
    """Execute multiple commands as a single undoable operation."""

    def __init__(self, commands: list[Command], desc: str = "Multiple actions") -> None:
        self.commands = commands
        self._desc = desc

    def execute(self, state: EditorState) -> None:
        for cmd in self.commands:
            cmd.execute(state)

    def undo(self, state: EditorState) -> None:
        for cmd in reversed(self.commands):
            cmd.undo(state)

    def description(self) -> str:
        return self._desc


class Clipboard:
    """Clipboard for copy/cut/paste of points."""

    def __init__(self) -> None:
        self.points: list[tuple[float, float]] = []
        self.source_region: str | None = None

    def copy(self, state: EditorState) -> None:
        """Copy selected points to the clipboard."""
        if not state.selected_points:
            return
        self.points = []
        self.source_region = None
        for region_name, index in sorted(state.selected_points):
            if region_name in state.regions and index < len(state.regions[region_name]):
                self.points.append(state.regions[region_name][index])
                self.source_region = region_name

    def cut(self, state: EditorState) -> None:
        """Copy selected points and remove them (undoable)."""
        if not state.selected_points or state.history is None:
            return
        self.copy(state)

        # Build removal commands in reverse index order to maintain indices
        removals: list[Command] = []
        for region_name, index in sorted(state.selected_points, reverse=True):
            if region_name in state.regions and index < len(state.regions[region_name]):
                point = state.regions[region_name][index]
                removals.append(RemovePointCommand(region_name, index, point))

        if removals:
            composite = CompositeCommand(removals, "Cut points")
            state.history.execute(composite, state)
            state.selected_points.clear()

    def paste(self, state: EditorState) -> None:
        """Paste clipboard points into the active region (undoable)."""
        if not self.points or state.active_region is None or state.history is None:
            return
        if state.active_region not in state.regions:
            return

        # Offset pasted points slightly to distinguish from originals
        offset_points = [(x + 5.0, y + 5.0) for x, y in self.points]
        insert_index = len(state.regions[state.active_region])
        cmd = PastePointsCommand(state.active_region, insert_index, offset_points)
        state.history.execute(cmd, state)

        # Select the pasted points
        state.selected_points.clear()
        for i in range(len(offset_points)):
            state.selected_points.add((state.active_region, insert_index + i))

    def has_content(self) -> bool:
        return len(self.points) > 0
