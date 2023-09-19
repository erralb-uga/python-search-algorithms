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


# Graph : a data structure that can tell me the neighbors for each graph location. A weighted graph also gives a cost of moving along an edge.
class SimpleGraph:
    def __init__(self):
        self.edges: dict[Location, list[Location]] = {}
    
    def neighbors(self, id: Location) -> list[Location]:
        return self.edges[id]


# example_graph : a simple graph with six nodes and eight edges.
example_graph = SimpleGraph()
example_graph.edges = {
    'A': ['B'], # A is connected to B
    'B': ['C'], # B is connected to C
    'C': ['B', 'D', 'F'], # C is connected to B, D, and F
    'D': ['C', 'E'], # D is connected to C and E
    'E': ['F'], # E is connected to F
    'F': [], # F is connected to nothing
}


import collections

# Queue a data structure used by the search algorithm to decide the order in which to process the graph locations.
class Queue:
    def __init__(self):
        self.elements = collections.deque()
    
    def empty(self) -> bool:
        return not self.elements
    
    def put(self, x: T):
        self.elements.append(x)
    
    def get(self) -> T:
        return self.elements.popleft()



# Search :an algorithm that takes a graph, a starting graph location, and optionally a goal graph location, and calculates some useful information (reached, parent pointer, distance) for some or all graph locations.
def breadth_first_search(graph: Graph, start: Location):
    # print out what we find
    frontier = Queue()
    frontier.put(start)
    reached: dict[Location, bool] = {}
    reached[start] = True
    
    while not frontier.empty():
        current: Location = frontier.get()
        print("  Visiting %s" % current)
        for next in graph.neighbors(current):
            if next not in reached:
                frontier.put(next)
                reached[next] = True



# Run the search algorithm on the example graph.
print('Reachable from A:')
breadth_first_search(example_graph, 'A')
print('Reachable from E:')
breadth_first_search(example_graph, 'E')