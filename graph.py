from node import Node, AddNeighbor, Distance
from segment import Segment
from path import Path, AddNodeToPath

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
            if line.lower() in ("[nodos]", "[nodes]"):
                mode = "nodes"
                continue
            elif line.lower() in ("[segmentos]", "[segments]"):
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
                    pass
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

def LoadAirspaceAsGraph(nav_file, seg_file, aer_file=None):
    from airspace_data import AirSpace

    airspace = AirSpace()
    if aer_file:
        airspace.load_from_files(nav_file, seg_file, aer_file)
    else:
        airspace.load_from_files(nav_file, seg_file)

    graph = Graph()
    navpoint_map = {}

    for np_id, np in airspace.navpoints.items():
        x = float(np.longitude) * 111
        y = float(np.latitude) * 111
        node = Node(np.name, x, y)
        AddNode(graph, node)
        navpoint_map[int(np.number)] = node

    for seg in airspace.navsegments:
        origin_id = seg.origin_number
        dest_id = seg.destination_number

        o = navpoint_map.get(origin_id)
        d = navpoint_map.get(dest_id)

        if o is None:
            o = Node(str(origin_id), 0.0, 0.0)
            AddNode(graph, o)
            navpoint_map[origin_id] = o

        if d is None:
            d = Node(str(dest_id), 0.0, 0.0)
            AddNode(graph, d)
            navpoint_map[dest_id] = d

        graph.segments.append(Segment(f"{o.name}-{d.name}", o, d))
        AddNeighbor(o, d)

    return graph

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    graph = LoadAirspaceAsGraph("cat_nav.txt", "cat_seg.txt", "cat_aer.txt")

    print(f"Nodos: {len(graph.nodes)}")
    print(f"Segmentos: {len(graph.segments)}")

    fig, ax = plt.subplots()

    for seg in graph.segments:
        ax.annotate(
            '',
            xy=(seg.destination.x, seg.destination.y),
            xytext=(seg.origin.x, seg.origin.y),
            arrowprops=dict(arrowstyle='->', color='black', lw=0.5, alpha=0.7)
        )

    for node in graph.nodes:
        ax.plot(node.x, node.y, 'bo')
        ax.text(node.x + 0.1, node.y + 0.1, node.name, fontsize=6)

    ax.set_title("Visualización de Grafo Aéreo")
    ax.axis("equal")
    plt.grid(True)
    plt.show()
