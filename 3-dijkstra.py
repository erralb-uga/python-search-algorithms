# Sample code from https://www.redblobgames.com/
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>


from __future__ import annotations
from typing import Protocol, Iterator, Tuple, TypeVar, Optional
T = TypeVar('T')

# Locations : a simple value (int, string, tuple, etc.) that labels locations in the graph.
Location = TypeVar('Location')
class Graph(Protocol):
    def neighbors(self, id: Location) -> list[Location]: pass

# Grids can be expressed as graphs too. I’ll now define a new graph called SquareGrid, with GridLocation being a tuple (x: int, y: int) that labels each location in the grid.
GridLocation = Tuple[int, int]

class SquareGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.walls: list[GridLocation] = []
    
    def in_bounds(self, id: GridLocation) -> bool:
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
    
    def passable(self, id: GridLocation) -> bool:
        return id not in self.walls
    
    def neighbors(self, id: GridLocation) -> Iterator[GridLocation]:
        (x, y) = id
        neighbors = [(x+1, y), (x-1, y), (x, y-1), (x, y+1)] # E W N S

        if (x + y) % 2 == 0: neighbors.reverse() # S N W E
        results = filter(self.in_bounds, neighbors)
        results = filter(self.passable, results)
        return results

# utility functions for dealing with square grids
def from_id_width(id, width):
    return (id % width, id // width)

def draw_tile(graph, id, style):
    r = " . "
    if 'number' in style and id in style['number']: r = " %-2d" % style['number'][id]
    if 'point_to' in style and style['point_to'].get(id, None) is not None:
        (x1, y1) = id
        (x2, y2) = style['point_to'][id]
        if x2 == x1 + 1: r = " > "
        if x2 == x1 - 1: r = " < "
        if y2 == y1 + 1: r = " v "
        if y2 == y1 - 1: r = " ^ "
    if 'path' in style and id in style['path']:   r = " @ "
    if 'start' in style and id == style['start']: r = " A "
    if 'goal' in style and id == style['goal']:   r = " Z "
    if id in graph.walls: r = "###"
    return r

def draw_grid(graph, **style):
    print("___" * graph.width)
    for y in range(graph.height):
        for x in range(graph.width):
            print("%s" % draw_tile(graph, (x, y), style), end="")
        print()
    print("~~~" * graph.width)

# Graph with weights
# A regular graph tells me the neighbors of each node. A weighted graph also tells me the cost of moving along each edge. I’m going to add a cost(from_node, to_node) function that tells us the cost of moving from location from_node to its neighbor to_node. Here’s the interface:
class WeightedGraph(Graph):
    def cost(self, from_id: Location, to_id: Location) -> float: pass

# Let’s implement the interface with a grid that uses grid locations and stores the weights in a dict:
class GridWithWeights(SquareGrid):
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.weights: dict[GridLocation, float] = {}
    
    def cost(self, from_node: GridLocation, to_node: GridLocation) -> float:
        return self.weights.get(to_node, 1)

# And here’s an example of a grid with weights:
diagram4 = GridWithWeights(10, 10)
diagram4.walls = [(1, 7), (1, 8), (2, 7), (2, 8), (3, 7), (3, 8)]
diagram4.weights = {loc: 5 for loc in [(3, 4), (3, 5), (4, 1), (4, 2),
                                       (4, 3), (4, 4), (4, 5), (4, 6),
                                       (4, 7), (4, 8), (5, 1), (5, 2),
                                       (5, 3), (5, 4), (5, 5), (5, 6),
                                       (5, 7), (5, 8), (6, 2), (6, 3),
                                       (6, 4), (6, 5), (6, 6), (6, 7),
                                       (7, 3), (7, 4), (7, 5)]}

print("Grid before search (costs are not drawn, just the grid)")
draw_grid(diagram4) # uncomment to see the grid


# Queue with priorities
# A priority queue associates with each item a number called a “priority”. When returning an item, it picks the one with the lowest number.

# insert : Add item to queue
# remove : Remove item with the lowest number
# reprioritize : (optional) Change an existing item’s priority to a lower number
import heapq

class PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[float, T]] = []
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, item: T, priority: float):
        heapq.heappush(self.elements, (priority, item))
    
    def get(self) -> T:
        return heapq.heappop(self.elements)[1]


# Search
# Here’s a tricky bit about the implementation: once we add movement costs it’s possible to visit a location again, with a better cost_so_far. That means the line if next not in came_from won’t work. Instead, have to check if the cost has gone down since the last time we reached. 

def dijkstra_search(graph: WeightedGraph, start: Location, goal: Location):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from: dict[Location, Optional[Location]] = {}
    cost_so_far: dict[Location, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.empty():
        current: Location = frontier.get()
        
        if current == goal:
            break
        
        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost
                frontier.put(next, priority)
                came_from[next] = current
    
    return came_from, cost_so_far


# Finally, after searching I need to build the path:

def reconstruct_path(came_from: dict[Location, Location],
                     start: Location, goal: Location) -> list[Location]:

    current: Location = goal
    path: list[Location] = []
    if goal not in came_from: # no path was found
        return []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start) # optional
    path.reverse() # optional
    return path


start, goal = (1, 4), (8, 3)
came_from, cost_so_far = dijkstra_search(diagram4, start, goal)
print('Explore grid with Dijkstra, A is the starting point, Z the goal')
draw_grid(diagram4, point_to=came_from, start=start, goal=goal)
print()
print('Draw found path with @ symbols')
draw_grid(diagram4, path=reconstruct_path(came_from, start=start, goal=goal))