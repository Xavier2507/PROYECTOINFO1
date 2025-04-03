from graph import Graph, AddNode, AddSegment
from node import Node

def create_example_graph():
    g = Graph()
    AddNode(g, Node("A", 0, 0))
    AddNode(g, Node("B", 1, 1))
    AddNode(g, Node("C", 2, 0))
    AddSegment(g, "A", "B")
    AddSegment(g, "A", "C")
    return g

def create_custom_graph():
    g = Graph()
    AddNode(g, Node("X", 0, 0))
    AddNode(g, Node("Y", 1, 2))
    AddNode(g, Node("Z", 2, 1))
    AddSegment(g, "X", "Y")
    AddSegment(g, "Y", "Z")
    AddSegment(g, "Z", "X")
    return g
