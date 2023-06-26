"""
Classic A-star algorithm for path finding.
"""
import math
from typing import (
    cast,
    List,
    Optional,
    Set,
    Tuple,
    Union,
    Dict
)

from arcade import (
    Sprite, SpriteList,
    check_for_collision_with_list,
    get_sprites_at_point
)
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
    """
    Return if position is blocked

    :param Point position: position to put moving_sprite at
    :param Sprite moving_sprite: Sprite to use
    :param SpriteList blocking_sprites: List of Sprites to check against

    :return: If the Sprite would hit anything in blocking_sprites at the position
    """
    original_pos = moving_sprite.position
    moving_sprite.position = position
    hit_list = check_for_collision_with_list(moving_sprite, blocking_sprites)
    moving_sprite.position = original_pos
    return len(hit_list) > 0


def _heuristic(start: Point, goal: Point) -> float:
    """
    Returns a heuristic value for the passed points.

    :param Point start: The 1st point to compare
    :param Point goal: The 2nd point to compare

    :return: The heuristic of the 2 points
    """
    # Use Chebyshev distance heuristic if we can move one square either
    # adjacent or diagonal
    d = 1
    d2 = 1
    dx = abs(start[0] - goal[0])
    dy = abs(start[1] - goal[1])
    return d * (dx + dy) + (d2 - 2 * d) * min(dx, dy)


class _AStarGraph(object):
    """
    A grid which tracks 2 barriers and a moving sprite.

    :param Union[List, Tuple, Set] barriers: Is turned into a set, and then used for _AStarSearch
    :param int left: Far left side x value
    :param int right: Far right side x value
    :param int bottom: Far bottom side y value
    :param int top: Far top side y value
    """

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
        """
        Return neighbors for this point according to ``self.movement_directions``

        These are not guaranteed to be reachable or valid points.

        :param Point pos: Which position to search around

        :return: Returns vertexes around the point
        """
        n = []
        # Moves allow link a chess king
        for dx, dy in self.movement_directions:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if x2 < self.left or x2 > self.right or y2 < self.bottom or y2 > self.top:
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, a: Point, b: Point) -> float:
        """
        Returns a float of the cost to move

        Moving diagonally costs more than to the side.
        A barrier's cost is float("inf) so that that
        the Algorithm will never go on it

        :param Point a: The 1st point to compare
        :param Point b: The 2nd point to compare

        :return: The move cost of moving between of the 2 points
        """
        if b in self.barriers:
            return float('inf')  # Infitely high cost to enter barrier squares

        elif a[0] == b[0] or a[1] == b[1]:
            return 1  # Normal movement cost
        else:
            return 1.42


def _AStarSearch(start: Point, end: Point, graph: _AStarGraph) -> Optional[List[Point]]:
    """
    Returns a path from start to end using the AStarSearch Algorithm

    Graph is used to check for barriers.

    :param Point start: point to start at
    :param Point end: point to end at

    :return: The path from start to end. Returns None if is path is not found
    """
    G: Dict[Point, float] = {}  # Actual movement cost to each position from the start position
    F: Dict[Point, float] = {}  # Estimated movement cost of start to end going via this position

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
        current_fscore = math.inf
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
    """Makes Point pos smaller by grid_size"""
    return int(pos[0] // grid_size), int(pos[1] // grid_size)


def _expand(pos: Point, grid_size: float):
    """Makes Point pos larger by grid_size"""
    return int(pos[0] * grid_size), int(pos[1] * grid_size)


class AStarBarrierList:
    """
    Class that manages a list of barriers that can be encountered during
    A* path finding.

    :param BasicSprite moving_sprite: Sprite that will be moving
    :param SpriteList blocking_sprites: Sprites that can block movement
    :param int grid_size: Size of the grid, in pixels
    :param int left: Left border of playing field
    :param int right: Right border of playing field
    :param int bottom: Bottom of playing field
    :param int top: Top of playing field
    :param Optional[Set] barrier_list: SpriteList of barriers to use in _AStarSearch, None if not recalculated
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
                         diagonal_movement: bool=True) -> Optional[List[Point]]:
    """
    Calculates the path using AStarSearch Algorithm and returns the path

    :param Point start_point: Where it starts
    :param Point end_point: Where it ends
    :param AStarBarrierList astar_barrier_list: AStarBarrierList with the boundries to use in the AStarSearch Algorithm
    :param bool diagonal_movement: Whether of not to use diagonals in the AStarSearch Algorithm

    :return: List of points(the path), or None if no path is found
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
    return cast(List[Point], revised_result)


def has_line_of_sight(observer: Point,
                      target: Point,
                      walls: SpriteList,
                      max_distance: float = float("inf"),
                      check_resolution: int = 2) -> bool:
    """
    Determine if we have line of sight between two points.

    :param Point observer: Start position
    :param Point target: End position position
    :param SpriteList walls: List of all blocking sprites
    :param int max_distance: Max distance point 1 can see
    :param int check_resolution: Check every x pixels for a sprite. Trade-off between accuracy and speed.

    .. warning:: Try to make sure spatial hashing is enabled on ``walls``!

                 If spatial hashing is not enabled, this function may run
                 very slowly!

    :return: Whether or not oberver to target is blocked by any wall in walls
    """
    if max_distance <= 0:
        raise ValueError("max_distance must be greater than zero")
    distance = get_distance(observer[0], observer[1],
                            target[0], target[1])
    steps = int(distance // check_resolution)
    for step in range(steps + 1):
        step_distance = step * check_resolution
        u = step_distance / distance
        midpoint = lerp_vec(observer, target, u)
        if step_distance > max_distance:
            return False
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
