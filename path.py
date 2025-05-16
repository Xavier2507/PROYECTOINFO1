from node import Distance

class Path:
    def __init__(self, nodes=None):
        self.nodes = nodes if nodes else []

    def __str__(self):
        names = " → ".join(n.name for n in self.nodes)
        return f"Path({names})"

    def AddNode(self, node):
        self.nodes.append(node)

    def ContainsNode(self, node):
        return node in self.nodes

    def Cost(self):
        total = 0
        for i in range(len(self.nodes) - 1):
            total += Distance(self.nodes[i], self.nodes[i + 1])
        return total

    def LastNode(self):
        return self.nodes[-1] if self.nodes else None

def AddNodeToPath(path, node):
    new_path = Path(path.nodes.copy())
    new_path.AddNode(node)
    return new_path

def ContainsNode(path, node):
    return node in path.nodes

def CostToNode(path, node):
    if node not in path.nodes:
        return -1
    index = path.nodes.index(node)
    total = 0
    for i in range(index):
        total += Distance(path.nodes[i], path.nodes[i + 1])
    return total

def PlotPath(graph, path):
    import matplotlib.pyplot as plt
    for segment in graph.segments:
        x = [segment.origin.x, segment.destination.x]
        y = [segment.origin.y, segment.destination.y]
        plt.plot(x, y, 'k-', alpha=0.2)
    for node in graph.nodes:
        plt.plot(node.x, node.y, 'ko')
        plt.text(node.x + 0.1, node.y + 0.1, node.name, fontsize=9)


    for i in range(len(path.nodes) - 1):
        n1 = path.nodes[i]
        n2 = path.nodes[i + 1]
        x = [n1.x, n2.x]
        y = [n1.y, n2.y]
        plt.plot(x, y, 'r-', linewidth=2)

    plt.axis('equal')
    plt.show()
