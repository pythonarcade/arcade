"""
Path-related functions.

"""
from arcade import Point
from arcade import SpriteList
from arcade import get_distance
from arcade import lerp_vec
from arcade import get_sprites_at_point
from arcade import check_for_collision_with_list


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

    def __init__(self, barriers, left, right, bottom, top):
        self.barriers = barriers
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom

    def heuristic(self, start, goal):
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
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
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
        for pos in openVertices:
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
        for neighbour in graph.get_vertex_neighbours(current):
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

    return None


def _collapse(pos, grid_size):
    return int(pos[0] // grid_size),  int(pos[1] // grid_size)

def _expand(pos, grid_size):
    return int(pos[0] * grid_size),  int(pos[1] * grid_size)


class BarrierList:
    def __init__(self, moving_sprite, blocking_sprites, grid_size, left, right, bottom, top):
        self.grid_size = grid_size
        self.bottom = bottom
        self.top = top
        self.left = left
        self.right = right
        original_pos = moving_sprite.position
        barrier_list = set()
        for cx in range(left, right + 1):
            for cy in range(bottom, top + 1):
                cpos = cx, cy
                pos = _expand(cpos, grid_size)
                if len(get_sprites_at_point(pos, blocking_sprites)) > 0:
                    barrier_list.add(cpos)
                moving_sprite.position = pos
                if len(check_for_collision_with_list(moving_sprite, blocking_sprites)) > 0:
                    barrier_list.add(cpos)

        moving_sprite.position = original_pos

        self.barrier_list = barrier_list


def astar(start, end, bl:BarrierList):

    grid_size = bl.grid_size
    mod_start = _collapse(start, grid_size)
    mod_end = _collapse(end, grid_size)

    left = bl.left
    right = bl.right

    bottom = bl.bottom
    top = bl.top

    # print("Start:", mod_start, "End:", mod_end)
    # print("Boundaries:", left, right, bottom, top)

    barrier_list = bl.barrier_list

    # print("Barriers:", barrier_list)
    graph = _AStarGraph(barrier_list, left, right, bottom, top)
    result = _AStarSearch(mod_start, mod_end, graph)
    # print("Result: ", result)
    if result is None:
        return None

    revised_result = []
    for p in result:
        revised_result.append(_expand(p, grid_size))
    return revised_result
