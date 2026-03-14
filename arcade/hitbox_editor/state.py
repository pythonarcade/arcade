"""Editor state model for the HitBox Editor."""

from __future__ import annotations

import enum
from pathlib import Path
from typing import TYPE_CHECKING

import arcade
from arcade.hitbox import HitBox

if TYPE_CHECKING:
    from arcade.hitbox_editor.history import Clipboard, CommandHistory


class ToolMode(enum.Enum):
    ADD = "add"
    SELECT = "select"
    DELETE = "delete"


class EditorState:
    """Central data model for the hitbox editor.

    All mutations should go through the CommandHistory so they can be undone.
    """

    def __init__(self) -> None:
        self.regions: dict[str, list[tuple[float, float]]] = {}
        self.active_region: str | None = None
        self.selected_points: set[tuple[str, int]] = set()
        self.tool_mode: ToolMode = ToolMode.ADD
        self.texture: arcade.Texture | None = None
        self.texture_path: Path | None = None

        # These are set after construction to avoid circular imports
        self.history: CommandHistory | None = None
        self.clipboard: Clipboard | None = None

        # Cursor position in world coordinates (for preview drawing)
        self.cursor_world: tuple[float, float] = (0.0, 0.0)

        # Point pick threshold in world units (adjusted for zoom by the view)
        self.pick_threshold: float = 15.0

        # Selection rectangle in world coords (x1, y1, x2, y2) while drag-selecting
        self.selection_rect: tuple[float, float, float, float] | None = None

    def load_texture(self, path: str | Path) -> None:
        """Load a texture from a file path."""
        path = Path(path)
        self.texture = arcade.load_texture(str(path))
        self.texture_path = path

    def load_hitbox(self, path: str | Path) -> None:
        """Load hitbox regions from a JSON file."""
        hb = HitBox.load(path)
        self.regions = {
            name: [tuple(p) for p in pts]
            for name, pts in hb.regions.items()
        }
        if self.regions:
            self.active_region = next(iter(self.regions))
        else:
            self.active_region = None
        self.selected_points.clear()

    def to_hitbox(self) -> HitBox:
        """Convert current state to a HitBox instance."""
        return HitBox({name: list(pts) for name, pts in self.regions.items()})

    def find_points_in_rect(
        self, x1: float, y1: float, x2: float, y2: float
    ) -> set[tuple[str, int]]:
        """Find all points within the given rectangle.

        Returns set of (region_name, point_index) tuples.
        """
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)

        result: set[tuple[str, int]] = set()
        for region_name, points in self.regions.items():
            for i, (px, py) in enumerate(points):
                if min_x <= px <= max_x and min_y <= py <= max_y:
                    result.add((region_name, i))
        return result

    def find_nearest_point(
        self, x: float, y: float, threshold: float
    ) -> tuple[str, int] | None:
        """Find the nearest point within threshold distance.

        Returns (region_name, point_index) or None.
        """
        best: tuple[str, int] | None = None
        best_dist = threshold * threshold  # compare squared distances

        for region_name, points in self.regions.items():
            for i, (px, py) in enumerate(points):
                dist_sq = (px - x) ** 2 + (py - y) ** 2
                if dist_sq < best_dist:
                    best_dist = dist_sq
                    best = (region_name, i)

        return best

    def find_nearest_edge(
        self, x: float, y: float, threshold: float
    ) -> tuple[str, int] | None:
        """Find the nearest edge within threshold distance.

        Returns (region_name, insert_index) where insert_index is the index
        at which a new point should be inserted, or None.
        """
        best: tuple[str, int] | None = None
        best_dist = threshold * threshold

        for region_name, points in self.regions.items():
            n = len(points)
            if n < 2:
                continue
            for i in range(n):
                ax, ay = points[i]
                bx, by = points[(i + 1) % n]
                dist_sq = _point_to_segment_dist_sq(x, y, ax, ay, bx, by)
                if dist_sq < best_dist:
                    best_dist = dist_sq
                    best = (region_name, (i + 1) % n if (i + 1) < n else n)

        return best


def _point_to_segment_dist_sq(
    px: float, py: float,
    ax: float, ay: float,
    bx: float, by: float,
) -> float:
    """Squared distance from point (px, py) to segment (ax, ay)-(bx, by)."""
    dx, dy = bx - ax, by - ay
    len_sq = dx * dx + dy * dy
    if len_sq == 0:
        return (px - ax) ** 2 + (py - ay) ** 2

    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / len_sq))
    proj_x = ax + t * dx
    proj_y = ay + t * dy
    return (px - proj_x) ** 2 + (py - proj_y) ** 2
