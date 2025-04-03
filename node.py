import math

class Node:
    def __init__(self, name, x, y):
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.neighbors = []

    def __str__(self):
        return f"Node({self.name}, {self.x}, {self.y})"

def AddNeighbor(n1, n2):
    if n2 in n1.neighbors:
        return False
    n1.neighbors.append(n2)
    return True

def Distance(n1, n2):
    dx = n1.x - n2.x
    dy = n1.y - n2.y
    return math.sqrt(dx**2 + dy**2)
