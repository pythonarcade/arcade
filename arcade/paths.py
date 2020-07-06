"""
Path-related functions.

"""
from arcade import Point
from arcade import get_distance
from arcade import lerp_vec
from arcade import get_sprites_at_point
from arcade import check_for_collision_with_list
from arcade import Sprite
from arcade import SpriteList

def has_line_of_sight(point_1: Point,
                      point_2: Point,
                      walls: SpriteList,
                      max_distance: int = -1,
                      check_resolution: int = 2):
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


"""
Classic A-star algorithm for path finding.
"""

def _spot_is_blocked(position, moving_sprite, blocking_sprites):
    original_pos = moving_sprite.position
    moving_sprite.position = position
    hit_list = check_for_collision_with_list(moving_sprite, blocking_sprites)
    moving_sprite.position = original_pos
    if len(hit_list) > 0:
        return True
    else:
        return False


class _AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self, barriers, left, right, bottom, top, diagonal_movement):
        self.barriers = barriers
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

        if diagonal_movement:
            self.movement_directions = (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)
        else:
            self.movement_directions = (1, 0), (-1, 0), (0, 1), (0, -1)

    def heuristic(self, start, goal):
        """

        Args:
            start:
            goal:

        Returns:

        """
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        D = 1
        D2 = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)

    def get_vertex_neighbours(self, pos):
        n = []
        # Moves allow link a chess king
        for dx, dy in self.movement_directions:
            x2 = pos[0] + dx
            y2 = pos[1] + dy
            if x2 < self.left or x2 > self.right or y2 < self.bottom or y2 > self.top:
                continue
            n.append((x2, y2))
        return n

    def move_cost(self, a, b):
        if b in self.barriers:
            # print("Ping")
            return 10  # Extremely high cost to enter barrier squares

        elif a[0] == b[0] or a[1] == b[1]:
            return 1
        else:
            return 1.414


        return 1  # Normal movement cost


def _AStarSearch(start, end, graph):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)

    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    count = 0
    while len(openVertices) > 0:
        count += 1
        if count > 2500:
            break
        # Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        for pos in sorted(openVertices):
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                current = pos

        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            if F[end] >= 10000:
                return None
            else:
                return path
            # return path, F[end]  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in sorted(graph.get_vertex_neighbours(current)):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively
            candidateG = G[current] + graph.move_cost(current, neighbour)

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex
            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H

    # Out-of-bounds
    return None


def _collapse(pos, grid_size):
    return int(pos[0] // grid_size),  int(pos[1] // grid_size)

def _expand(pos, grid_size):
    return int(pos[0] * grid_size),  int(pos[1] * grid_size)


class AStarBarrierList:
    """
    Class that manages a list of barriers that can be encountered during
    A* path finding.
    """
    def __init__(self,
                 moving_sprite: Sprite,
                 blocking_sprites: SpriteList,
                 grid_size: int,
                 left: int,
                 right: int,
                 bottom: int,
                 top: int):
        """
        :param Sprite moving_sprite: Sprite that will be moving
        :param SpriteList blocking_sprites: Sprites that can block movement
        :param int grid_size: Size of the grid, in pixels
        :param int left: Left border of playing field
        :param int right: Right border of playing field
        :param int bottom: Bottom of playing field
        :param int top: Top of playing field
        """

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

    graph = _AStarGraph(barrier_list, left, right, bottom, top, diagonal_movement)
    result = _AStarSearch(mod_start, mod_end, graph)

    if result is None:
        return None

    # Currently 'result' is in grid locations. We need to convert them to pixel
    # locations.
    revised_result = [_expand(p, grid_size) for p in result]
    return revised_result
