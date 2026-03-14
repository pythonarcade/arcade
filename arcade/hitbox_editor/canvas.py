"""Canvas rendering for the HitBox Editor."""

from __future__ import annotations

from typing import TYPE_CHECKING

import arcade
from arcade import LBWH, XYWH
from arcade.camera import Camera2D

if TYPE_CHECKING:
    from arcade.hitbox_editor.state import EditorState, ToolMode

# Color palette for different regions
REGION_COLORS = [
    (255, 50, 50, 200),    # Red
    (50, 255, 50, 200),    # Green
    (50, 50, 255, 200),    # Blue
    (255, 255, 50, 200),   # Yellow
    (255, 50, 255, 200),   # Magenta
    (50, 255, 255, 200),   # Cyan
    (255, 128, 0, 200),    # Orange
    (128, 0, 255, 200),    # Purple
    (0, 255, 128, 200),    # Spring green
    (255, 128, 128, 200),  # Light red
]

HANDLE_RADIUS = 5.0
SELECTED_HANDLE_RADIUS = 7.0
HANDLE_COLOR = (255, 255, 255, 220)
SELECTED_HANDLE_COLOR = (255, 255, 0, 255)
PREVIEW_LINE_COLOR = (200, 200, 200, 120)
CHECKER_COLOR_A = (80, 80, 80, 255)
CHECKER_COLOR_B = (60, 60, 60, 255)


class CanvasRenderer:
    """Handles rendering the texture, polygons, and handles on the canvas."""

    def __init__(self, state: EditorState, window: arcade.Window) -> None:
        self.state = state
        self.window = window
        self.camera = Camera2D()
        self._zoom_level: float = 1.0

    @property
    def zoom(self) -> float:
        return self._zoom_level

    def screen_to_world(self, sx: float, sy: float) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        result = self.camera.unproject((sx, sy))
        return (result.x, result.y)

    def pan(self, dx: float, dy: float) -> None:
        """Pan the camera by screen-space delta."""
        # Convert screen delta to world delta (inverse of zoom)
        world_dx = -dx / self._zoom_level
        world_dy = -dy / self._zoom_level
        pos = self.camera.position
        self.camera.position = (pos[0] + world_dx, pos[1] + world_dy)

    def zoom_at(self, factor: float, screen_x: float, screen_y: float) -> None:
        """Zoom toward/away from screen point."""
        # Get world pos before zoom
        before = self.camera.unproject((screen_x, screen_y))

        # Apply zoom
        self._zoom_level *= factor
        self._zoom_level = max(0.05, min(50.0, self._zoom_level))
        self.camera.zoom = self._zoom_level

        # Get world pos after zoom
        after = self.camera.unproject((screen_x, screen_y))

        # Adjust position to keep the world point under the cursor
        pos = self.camera.position
        self.camera.position = (
            pos[0] + (before.x - after.x),
            pos[1] + (before.y - after.y),
        )

    def fit_texture(self, panel_width: int = 300) -> None:
        """Reset camera to fit the texture in the canvas area."""
        tex = self.state.texture
        if tex is None:
            self.camera.position = (0.0, 0.0)
            self._zoom_level = 1.0
            self.camera.zoom = 1.0
            return

        canvas_width = self.window.width - panel_width
        canvas_height = self.window.height

        if canvas_width <= 0 or canvas_height <= 0:
            return

        # Calculate zoom to fit texture with some padding
        padding = 0.9  # 90% of available space
        zoom_x = (canvas_width * padding) / tex.width
        zoom_y = (canvas_height * padding) / tex.height
        self._zoom_level = min(zoom_x, zoom_y)
        self.camera.zoom = self._zoom_level

        # Center camera on texture center, offset for the panel
        # The panel takes up the right side, so shift camera left slightly
        panel_world_offset = (panel_width / 2.0) / self._zoom_level
        self.camera.position = (panel_world_offset, 0.0)

    def draw(self, panel_width: int = 300) -> None:
        """Draw the full canvas: background, texture, regions, handles."""
        self.camera.use()

        self._draw_checkerboard(panel_width)

        if self.state.texture is not None:
            self._draw_texture()

        self._draw_regions()
        self._draw_selection_rect()
        self._draw_preview_line()

    def _draw_checkerboard(self, panel_width: int) -> None:
        """Draw a checkerboard pattern behind the texture area."""
        tex = self.state.texture
        if tex is None:
            return

        half_w = tex.width / 2
        half_h = tex.height / 2
        checker_size = 16.0

        y = -half_h
        row = 0
        while y < half_h:
            x = -half_w
            col = 0
            while x < half_w:
                w = min(checker_size, half_w - x)
                h = min(checker_size, half_h - y)
                color = CHECKER_COLOR_A if (row + col) % 2 == 0 else CHECKER_COLOR_B
                arcade.draw_rect_filled(LBWH(x, y, w, h), color)
                x += checker_size
                col += 1
            y += checker_size
            row += 1

    def _draw_texture(self) -> None:
        """Draw the loaded texture centered at origin."""
        tex = self.state.texture
        if tex is None:
            return
        rect = XYWH(0, 0, tex.width, tex.height)
        arcade.draw_texture_rect(tex, rect)

    def _draw_regions(self) -> None:
        """Draw all hitbox regions as colored polygons with handles."""
        region_names = list(self.state.regions.keys())
        zoom = self._zoom_level

        for idx, name in enumerate(region_names):
            points = self.state.regions[name]
            if not points:
                continue

            color = REGION_COLORS[idx % len(REGION_COLORS)]
            is_active = name == self.state.active_region

            # Draw faint fill for active region
            if is_active and len(points) >= 3:
                fill_color = (color[0], color[1], color[2], 45)
                arcade.draw_polygon_filled(points, fill_color)

            # Draw polygon outline
            if len(points) >= 2:
                line_width = 1.5
                if len(points) >= 3:
                    arcade.draw_polygon_outline(points, color, line_width)
                else:
                    arcade.draw_line(
                        points[0][0], points[0][1],
                        points[1][0], points[1][1],
                        color, line_width,
                    )

            # Draw point handles
            for i, (px, py) in enumerate(points):
                key = (name, i)
                if key in self.state.selected_points:
                    # Selected point: filled circle + white outline ring + crosshair
                    arcade.draw_circle_filled(
                        px, py,
                        SELECTED_HANDLE_RADIUS / zoom,
                        SELECTED_HANDLE_COLOR,
                    )
                    arcade.draw_circle_outline(
                        px, py,
                        (SELECTED_HANDLE_RADIUS + 3) / zoom,
                        (255, 255, 255, 255),
                        2 / zoom,
                    )
                    # Small crosshair through selected point
                    cross_len = 8.0 / zoom
                    arcade.draw_line(
                        px - cross_len, py, px + cross_len, py,
                        (255, 255, 255, 150), 1.0,
                    )
                    arcade.draw_line(
                        px, py - cross_len, px, py + cross_len,
                        (255, 255, 255, 150), 1.0,
                    )
                else:
                    arcade.draw_circle_filled(
                        px, py,
                        HANDLE_RADIUS / zoom,
                        HANDLE_COLOR,
                    )

    def _draw_selection_rect(self) -> None:
        """Draw the drag-to-select rectangle if active."""
        rect = self.state.selection_rect
        if rect is None:
            return

        x1, y1, x2, y2 = rect
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        w = abs(x2 - x1)
        h = abs(y2 - y1)
        if w < 0.1 or h < 0.1:
            return

        r = XYWH(cx, cy, w, h)
        arcade.draw_rect_filled(r, (100, 150, 255, 30))
        arcade.draw_rect_outline(r, (100, 150, 255, 180), 1.5)

    def _draw_preview_line(self) -> None:
        """Draw a preview line from the last point to the cursor in ADD mode."""
        from arcade.hitbox_editor.state import ToolMode

        if self.state.tool_mode != ToolMode.ADD:
            return
        if self.state.active_region is None:
            return

        points = self.state.regions.get(self.state.active_region, [])
        if not points:
            return

        cx, cy = self.state.cursor_world
        last = points[-1]
        arcade.draw_line(last[0], last[1], cx, cy, PREVIEW_LINE_COLOR, 1.0)

        # Also draw line from cursor back to first point (to show closing)
        if len(points) >= 2:
            first = points[0]
            arcade.draw_line(cx, cy, first[0], first[1], PREVIEW_LINE_COLOR, 1.0)
