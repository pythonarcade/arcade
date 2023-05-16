"""
Classic A-star algorithm for path finding.
"""
from typing import List, Optional, Set, Tuple, Union

from arcade import (Sprite, SpriteList, check_for_collision_with_list,
                    get_sprites_at_point)
from arcade.math import get_distance, lerp_vec
from arcade.types import Point

__all__ = [
    "AStarBarrierList",
    "astar_calculate_path",
    "has_line_of_sight"
]


def _spot_is_blocked(position: Point,
                     moving_sprite: Sprite,
                     blocking_sprites: SpriteList) -> bool:
    original_pos = moving_sprite.position
    moving_sprite.position = position
    hit_list = check_for_collision_with_list(moving_sprite, blocking_sprites)
    moving_sprite.position = original_pos
    return len(hit_list) > 0


def _heuristic(start: Point, goal: Point):
    """
    Returns the heuristic of the 2 poitns

    Args:
        start: The 1st point to compare
        goal: The 2nd point to compare

    Returns:
        The heuristic of the 2 points
    """
    # Use Chebyshev distance heuristic if we can move one square either
    # adjacent or diagonal
    d = 1
    d2 = 1
    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    return d * (dx + dy) + (d2 - 2 * d) * min(dx, dy)


class _AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self, barriers: Union[List, Tuple, Set],
                 left: int,
                 right: int,
                 bottom: int,
                 top: int,
                 diagonal_movement: bool):
        self.barriers = barriers if barriers is set else set(barriers)
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        if diagonal_movement:
            self.movement_directions = (  # type: ignore
                (1, 0), (-1, 0),
                (0, 1), (0, -1),
                (1, 1), (-1, 1),
                (1, -1), (-1, -1)
            )
        else:
            self.movement_directions = (1, 0), (-1, 0), (0, 1), (0, -1)  # type: ignore

    def get_vertex_neighbours(self, pos: Point) -> List[Tuple[float, float]]:
        n = []
        # Moves allow link a chess king
        for dx, dy in self.movement_directions:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if x2 < self.left or x2 > self.right or y2 < self.bottom or y2 > self.top:
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, a: Point, b: Point):
        if b in self.barriers:
            # print("Ping")
            return float('inf')  # Infitely high cost to enter barrier squares

        elif a[0] == b[0] or a[1] == b[1]:
            return 1  # Normal movement cost
        else:
            return 1.42


def _AStarSearch(start: Point, end: Point, graph: _AStarGraph) -> Optional[List[Point]]:
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    # Initialize starting values
    G[start] = 0
    F[start] = _heuristic(start, end)

    closed_vertices = set()
    open_vertices = {start}
    came_from = {}  # type: ignore

    count = 0
    while len(open_vertices) > 0:
        count += 1
        if count > 500:
            break
        # Get the vertex in the open list with the lowest F score
        current = None
        current_fscore = None
        for pos in sorted(open_vertices):
            if current is None or F[pos] < current_fscore:
                current_fscore = F[pos]
                current = pos

        # Check if we have reached the goal
        if current == end and current is not None:
            # Retrace our route backward
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)  # type: ignore
            path.reverse()
            if F[end] >= 10000:
                return None
            else:
                return path
            # return path, F[end]  # Done!

        # Mark the current vertex as closed
        open_vertices.remove(current)  # type: ignore
        closed_vertices.add(current)  # type: ignore

        # Update scores for vertices near the current position
        for neighbour in sorted(graph.get_vertex_neighbours(current)):  # type: ignore
            if neighbour in closed_vertices:
                continue  # We have already processed this node exhaustively
            candidate_g = G[current] + graph.move_cost(current, neighbour)  # type: ignore

            if neighbour not in open_vertices:
                open_vertices.add(neighbour)  # Discovered a new vertex
            elif candidate_g >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            came_from[neighbour] = current
            G[neighbour] = candidate_g
            h = _heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + h

    # Out-of-bounds
    return None


def _collapse(pos: Point, grid_size: float):
    return int(pos[0] // grid_size), int(pos[1] // grid_size)


def _expand(pos: Point, grid_size: float):
    return int(pos[0] * grid_size), int(pos[1] * grid_size)


class AStarBarrierList:
    """
    Class that manages a list of barriers that can be encountered during
    A* path finding.

    :param Sprite moving_sprite: Sprite that will be moving
    :param SpriteList blocking_sprites: Sprites that can block movement
    :param int grid_size: Size of the grid, in pixels
    :param int left: Left border of playing field
    :param int right: Right border of playing field
    :param int bottom: Bottom of playing field
    :param int top: Top of playing field
    """
    def __init__(self,
                 moving_sprite: Sprite,
                 blocking_sprites: SpriteList,
                 grid_size: int,
                 left: int,
                 right: int,
                 bottom: int,
                 top: int):

        self.grid_size = grid_size
        self.bottom = int(bottom // grid_size)
        self.top = int(top // grid_size)
        self.left = int(left // grid_size)
        self.right = int(right // grid_size)
        self.moving_sprite = moving_sprite
        self.blocking_sprites = blocking_sprites
        self.barrier_list = None

        self.recalculate()

    def recalculate(self):
        """
        Recalculate blocking sprites.
        """
        # --- Iterate through the blocking sprites and find where we are blocked

        # Save original location
        original_pos = self.moving_sprite.position
        # Create a set of barriers
        self.barrier_list = set()
        # Loop through the grid
        for cx in range(self.left, self.right + 1):
            for cy in range(self.bottom, self.top + 1):
                # Grid location
                cpos = cx, cy
                # Pixel location
                pos = _expand(cpos, self.grid_size)

                # See if we'll have a collision if our sprite is at this location
                self.moving_sprite.position = pos
                if len(check_for_collision_with_list(self.moving_sprite, self.blocking_sprites)) > 0:
                    self.barrier_list.add(cpos)

        # Restore original location
        self.moving_sprite.position = original_pos
        self.barrier_list = sorted(self.barrier_list)


def astar_calculate_path(start_point: Point,
                         end_point: Point,
                         astar_barrier_list: AStarBarrierList,
                         diagonal_movement=True):
    """
    :param Point start_point:
    :param Point end_point:
    :param AStarBarrierList astar_barrier_list:
    :param bool diagonal_movement:

    Returns: List

    """

    grid_size = astar_barrier_list.grid_size
    mod_start = _collapse(start_point, grid_size)
    mod_end = _collapse(end_point, grid_size)

    left = astar_barrier_list.left
    right = astar_barrier_list.right

    bottom = astar_barrier_list.bottom
    top = astar_barrier_list.top

    barrier_list = astar_barrier_list.barrier_list

    graph = _AStarGraph(barrier_list, left, right, bottom, top, diagonal_movement)  # type: ignore
    result = _AStarSearch(mod_start, mod_end, graph)

    if result is None:
        return None

    # Currently 'result' is in grid locations. We need to convert them to pixel
    # locations.
    revised_result = [_expand(p, grid_size) for p in result]
    return revised_result


def has_line_of_sight(point_1: Point,
                      point_2: Point,
                      walls: SpriteList,
                      max_distance: int = -1,
                      check_resolution: int = 2) -> bool:
    """
    Determine if we have line of sight between two points. Try to make sure
    that spatial hashing is enabled on the wall SpriteList or this will be
    very slow.

    :param Point point_1: Start position
    :param Point point_2: End position position
    :param SpriteList walls: List of all blocking sprites
    :param int max_distance: Max distance point 1 can see
    :param int check_resolution: Check every x pixels for a sprite. Trade-off
                                 between accuracy and speed.
    """
    distance = get_distance(point_1[0], point_1[1],
                            point_2[0], point_2[1])
    steps = int(distance // check_resolution)
    for step in range(steps + 1):
        step_distance = step * check_resolution
        u = step_distance / distance
        midpoint = lerp_vec(point_1, point_2, u)
        if max_distance != -1 and step_distance > max_distance:
            return False
        # print(point_1, point_2, step, u, step_distance, midpoint)
        sprite_list = get_sprites_at_point(midpoint, walls)
        if len(sprite_list) > 0:
            return False
    return True


# NOTE: Rewrite this
# def dda_step(start: Point, end: Point):
#     """
#     Bresenham's line algorithm

#     :param Point start:
#     :param Point end:
#     :return: List of points
#     """
#     x1, y1 = start
#     x2, y2 = end

#     dx = x2 - x1
#     dy = y2 - y1

#     steps = max(abs(dx), abs(dy))

#     x_inc = dx / steps
#     y_inc = dy / steps

#     x = x1
#     y = y1

#     points = []
#     for _ in range(steps):
#         points.append((int(x), int(y)))
#         x += x_inc
#         y += y_inc

#     return points
#     return points
