
from node import *
from segment import *
import matplotlib.pyplot as plt

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
    for s in g.segments:
        x = [s.origin.x, s.destination.x]
        y = [s.origin.y, s.destination.y]
        plt.plot(x, y, 'k-')
        plt.text((x[0]+x[1])/2, (y[0]+y[1])/2, f"{s.cost:.1f}", fontsize=8)
    for n in g.nodes:
        plt.plot(n.x, n.y, 'ko')
        plt.text(n.x+0.1, n.y+0.1, n.name, fontsize=9)
    plt.axis('equal')
    plt.show()

def PlotNode(g, nameOrigin):
    o = next((n for n in g.nodes if n.name == nameOrigin), None)
    if o is None:
        print("Nodo no encontrado")
        return False


    for n in g.nodes:
        color = 'blue' if n == o else 'green' if o in n.neighbors or n in o.neighbors else 'gray'
        plt.plot(n.x, n.y, 'o', color=color)
        plt.text(n.x + 0.1, n.y + 0.1, n.name, fontsize=9)


    for s in g.segments:
        if (s.origin == o and s.destination in o.neighbors) or (s.destination == o and s.origin in o.neighbors):
            x = [s.origin.x, s.destination.x]
            y = [s.origin.y, s.destination.y]
            plt.plot(x, y, 'r-')
            plt.text((x[0]+x[1])/2, (y[0]+y[1])/2, f"{s.cost:.1f}", fontsize=8)
        else:
            x = [s.origin.x, s.destination.x]
            y = [s.origin.y, s.destination.y]
            plt.plot(x, y, 'k-', alpha=0.2)

    plt.axis('equal')
    plt.show()
    return True

def LoadGraphFromFile(filename):
    g = Graph()
    with open(filename, 'r') as f:
        mode = None
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            if line.lower() == "[nodes]":
                mode = "nodes"
                continue
            if line.lower() == "[segments]":
                mode = "segments"
                continue

            parts = line.split()

            if mode == "nodes" and len(parts) == 3:
                name, x, y = parts
                AddNode(g, Node(name, float(x), float(y)))

            elif mode == "segments" and len(parts) == 2:
                origin, destination = parts
                AddSegment(g, origin, destination)

    return g

if __name__ == "__main__":
    print("Cargando grafo desde el archivo...")
    G2 = LoadGraphFromFile("grafo.txt")

    print("Nodos cargados:", [n.name for n in G2.nodes])
    print("Número de segmentos:", len(G2.segments))

    Plot(G2)
