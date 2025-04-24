import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from node import Node, AddNeighbor, Distance
from segment import Segment
from path import Path, AddNodeToPath, PlotPath

class Graph:
    def __init__(self):
        self.nodes = []
        self.segments = []

def AddNode(g, n):
    if n in g.nodes:
        return False
    g.nodes.append(n)
    return True

def AddSegment(g, nameOriginNode, nameDestinationNode):
    o = d = None
    for n in g.nodes:
        if n.name == nameOriginNode:
            o = n
        if n.name == nameDestinationNode:
            d = n
    if o is None or d is None:
        return False
    g.segments.append(Segment(f"{o.name}-{d.name}", o, d))
    AddNeighbor(o, d)
    return True

def GetClosest(g, x, y):
    p = Node('', x, y)
    return min(g.nodes, key=lambda n: Distance(n, p))

def Plot(g):
    fig, ax = plt.subplots()
    for s in g.segments:
        dx = s.destination.x - s.origin.x
        dy = s.destination.y - s.origin.y
        arrow = FancyArrowPatch((s.origin.x, s.origin.y), (s.destination.x, s.destination.y),
                                arrowstyle='->', color='black', linewidth=1.5, mutation_scale=10)
        ax.add_patch(arrow)
        mx = (s.origin.x + s.destination.x) / 2
        my = (s.origin.y + s.destination.y) / 2
        plt.text(mx, my, f"{s.cost:.1f}", fontsize=8, color='gray')

    for n in g.nodes:
        plt.plot(n.x, n.y, 'ko')
        plt.text(n.x + 0.1, n.y + 0.1, n.name, fontsize=9)

    plt.axis('equal')
    plt.title("Grafo con direccionalidad")
    plt.show()

def PlotNode(g, nameOrigin):
    o = next((n for n in g.nodes if n.name == nameOrigin), None)
    if o is None:
        print("Nodo no encontrado")
        return False

    fig, ax = plt.subplots()
    for n in g.nodes:
        color = 'blue' if n == o else 'green' if o in n.neighbors else 'gray'
        plt.plot(n.x, n.y, 'o', color=color)
        plt.text(n.x + 0.1, n.y + 0.1, n.name, fontsize=9)

    for s in g.segments:
        dx = s.destination.x - s.origin.x
        dy = s.destination.y - s.origin.y
        arrow = FancyArrowPatch((s.origin.x, s.origin.y), (s.destination.x, s.destination.y),
                                arrowstyle='->', color='red' if s.origin == o else 'black',
                                linewidth=1.5, mutation_scale=10, alpha=1 if s.origin == o else 0.3)
        ax.add_patch(arrow)
        mx = (s.origin.x + s.destination.x) / 2
        my = (s.origin.y + s.destination.y) / 2
        if s.origin == o:
            plt.text(mx, my, f"{s.cost:.1f}", fontsize=8, color='red')

    plt.axis('equal')
    plt.title(f"Vecinos desde {nameOrigin}")
    plt.show()
    return True

def LoadGraphFromFile(filename):
    graph = Graph()
    node_dict = {}
    pending_segments = []

    with open(filename, 'r') as file:
        mode = None
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.lower() == "[nodes]":
                mode = "nodes"
                continue
            elif line.lower() == "[segments]":
                mode = "segments"
                continue

            parts = line.split()
            if mode == "nodes" and len(parts) >= 3:
                name = parts[0]
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    node = Node(name, x, y)
                    graph.nodes.append(node)
                    node_dict[name] = node
                except ValueError:
                    print(f" Coordenadas inválidas para nodo: {line}")
            elif mode == "segments" and len(parts) >= 2:
                origin_name = parts[0]
                dest_name = parts[1]
                pending_segments.append((origin_name, dest_name))

    for origin_name, dest_name in pending_segments:
        origin = node_dict.get(origin_name)
        dest = node_dict.get(dest_name)
        if origin and dest:
            graph.segments.append(Segment(f"{origin.name}-{dest.name}", origin, dest))
            AddNeighbor(origin, dest)
        else:
            print(f"⚠ Segmento no creado: {origin_name} -> {dest_name} (nodo no encontrado)")

    return graph

def FindReachableNodes(g, originName):
    origin = next((n for n in g.nodes if n.name == originName), None)
    if origin is None:
        return []

    visited = set()
    queue = [origin]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for neighbor in current.neighbors:
            if neighbor not in visited:
                queue.append(neighbor)
    return list(visited)

def FindShortestPath(g, originName, destinationName):
    origin = next((n for n in g.nodes if n.name == originName), None)
    destination = next((n for n in g.nodes if n.name == destinationName), None)
    if origin is None or destination is None:
        return None

    current_paths = [Path([origin])]

    while current_paths:
        current_paths.sort(key=lambda p: p.Cost() + Distance(p.LastNode(), destination))
        current = current_paths.pop(0)
        last_node = current.LastNode()

        if last_node == destination:
            return current

        for neighbor in last_node.neighbors:
            if neighbor in current.nodes:
                continue
            new_path = AddNodeToPath(current, neighbor)
            current_paths.append(new_path)

    return None
