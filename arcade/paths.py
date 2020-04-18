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

# from constants import *
# from get_blocking_sprites import get_blocking_sprites

ITERATION_LIMIT = 50
GRID_SIZE = 16


class Node:
    """A node class for A* Path-finding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        result = abs(self.position[0] - other.position[0]) <= GRID_SIZE and abs(self.position[1] - other.position[1]) <= GRID_SIZE

        return result

def spot_is_blocked(position, moving_sprite, blocking_sprites):
    original_pos = moving_sprite.position
    moving_sprite.position = position
    hit_list = check_for_collision_with_list(moving_sprite, blocking_sprites)
    moving_sprite.position = original_pos
    if len(hit_list) > 0:
        return True
    else:
        return False

def astar(start, end, moving_sprite, blocking_sprites):
    """Returns a list of tuples as a path from the given start to the given end in the given maze"""

    # Create start and end node
    start_node = Node(None, start)
    start_node.g = start_node.h = start_node.f = 0
    end_node = Node(None, end)
    end_node.g = end_node.h = end_node.f = 0

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop counter used to break out if we work too hard
    loop_count = 0
    # Loop until you find the end or we've worked too hard
    while len(open_list) > 0:
        loop_count += 1
        if loop_count > ITERATION_LIMIT:
            # Ok, this is too hard. Give up.
            # print("BREAK!")
            return None

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children
        children = []
        for new_position in [
            (0, -GRID_SIZE),
            (0, GRID_SIZE),
            (-GRID_SIZE, 0),
            (GRID_SIZE, 0),
            (-GRID_SIZE, -GRID_SIZE),
            (-GRID_SIZE, GRID_SIZE),
            (GRID_SIZE, -GRID_SIZE),
            (GRID_SIZE, GRID_SIZE),
        ]:  # Adjacent squares

            # Get node position
            node_position = (
                current_node.position[0] + new_position[0],
                current_node.position[1] + new_position[1],
            )

            # Make sure within range
            # if node_position[0] > (len(maze) - 1)
            #   or node_position[0] < 0
            #   or node_position[1] > (len(maze[len(maze)-1]) -1)
            #   or node_position[1] < 0:
            #     continue

            # Make sure walkable terrain

            if spot_is_blocked(node_position, moving_sprite, blocking_sprites):
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                (child.position[1] - end_node.position[1]) ** 2
            )
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)