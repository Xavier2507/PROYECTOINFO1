from collections import deque
import heapq
import os
import platform
import subprocess
from typing import Dict, List, Optional, Set, Tuple


class Node:
    def __init__(self, name: str, x: float, y: float, is_airport: bool = False):
        self.name = name
        self.x = x
        self.y = y
        self.is_airport = is_airport
        self.neighbors: Set['Node'] = set()

    def __repr__(self):
        return f"Node({self.name}, {self.x}, {self.y})"

    def __eq__(self, other):
        return isinstance(other, Node) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Segment:
    def __init__(self, name: str, origin: Node, destination: Node):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.cost = ((origin.x - destination.x)**2 + (origin.y - destination.y)**2)**0.5

    def __repr__(self):
        return f"Segment({self.name}, cost={self.cost:.2f})"


class Graph:
    def __init__(self):
        self._nodes: Dict[str, Node] = {}
        self.segments: List[Segment] = []

    @property
    def nodes(self) -> List[Node]:
        return list(self._nodes.values())

    def add_node(self, node: Node) -> bool:
        if node.name in self._nodes:
            return False
        self._nodes[node.name] = node
        return True

    def add_segment(self, origin_name: str, dest_name: str) -> bool:
        o = self._nodes.get(origin_name)
        d = self._nodes.get(dest_name)
        if not o or not d:
            return False
        seg = Segment(f"{origin_name}-{dest_name}", o, d)
        self.segments.append(seg)
        o.neighbors.add(d)
        d.neighbors.add(o)
        return True

    def get_closest(self, x: float, y: float) -> Optional[Node]:
        if not self._nodes:
            return None
        return min(self._nodes.values(), key=lambda n: (n.x - x)**2 + (n.y - y)**2)

    def find_reachable(self, origin_name: str) -> List[Node]:
        origin = self._nodes.get(origin_name)
        if not origin:
            return []
        visited: Set[Node] = set()
        queue = deque([origin])
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            for nbr in node.neighbors:
                if nbr not in visited:
                    queue.append(nbr)
        return list(visited)

    def find_shortest_path(self, origin_name: str, dest_name: str) -> Optional[List[Node]]:
        origin = self._nodes.get(origin_name)
        dest = self._nodes.get(dest_name)
        if not origin or not dest:
            return None
        reachable = set(self.find_reachable(origin_name))
        if dest not in reachable:
            return None
        open_heap: List[Tuple[float, float, List[Node]]] = []
        heapq.heappush(open_heap, (self._heuristic(origin, dest), 0.0, [origin]))
        visited: Set[Node] = set()
        g_score: Dict[Node, float] = {origin: 0.0}
        while open_heap:
            _, cost, path = heapq.heappop(open_heap)
            node = path[-1]
            if node == dest:
                return path
            if node in visited:
                continue
            visited.add(node)
            for nbr in node.neighbors:
                tentative = cost + self._distance(node, nbr)
                if tentative < g_score.get(nbr, float('inf')):
                    g_score[nbr] = tentative
                    f = tentative + self._heuristic(nbr, dest)
                    heapq.heappush(open_heap, (f, tentative, path + [nbr]))
        return None

    @staticmethod
    def _distance(a: Node, b: Node) -> float:
        return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5

    @staticmethod
    def _heuristic(a: Node, b: Node) -> float:
        return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5

    def export_kml(self,
                   filename: str = 'graph.kml',
                   origin: Optional[Node] = None,
                   reachable: Optional[List[Node]] = None,
                   path: Optional[List[Node]] = None) -> None:
        reachable_set = set(reachable or [])
        path_pairs = set(zip(path or [], path[1:] if path else []))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
            # nodos
            for node in self._nodes.values():
                lon, lat = node.x / 111.0, node.y / 111.0
                if node == origin:
                    color = 'ff0000ff'
                elif node in reachable_set:
                    color = 'ff00ff00'
                elif node.is_airport:
                    color = 'ff00ffff'
                else:
                    color = 'ff000000'
                f.write(
                    f'<Placemark><name>{node.name}</name>'
                    f'<Style><IconStyle><color>{color}</color><scale>1.1</scale>'
                    '<Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href>'
                    '</Icon></IconStyle></Style>'
                    f'<Point><coordinates>{lon},{lat},0</coordinates></Point>'
                    '</Placemark>\n'
                )
            # segmentos
            for seg in self.segments:
                lon1, lat1 = seg.origin.x / 111.0, seg.origin.y / 111.0
                lon2, lat2 = seg.destination.x / 111.0, seg.destination.y / 111.0
                if (seg.origin, seg.destination) in path_pairs:
                    color = 'ff0000ff'
                elif seg.origin in reachable_set and seg.destination in reachable_set:
                    color = 'ff00ff00'
                else:
                    color = 'ffaaaaaa'
                f.write(
                    f'<Placemark><name>{seg.name}</name>'
                    f'<Style><LineStyle><color>{color}</color><width>3</width></LineStyle></Style>'
                    f'<LineString><tessellate>1</tessellate>'
                    f'<coordinates>{lon1},{lat1},0 {lon2},{lat2},0</coordinates>'
                    '</LineString></Placemark>\n'
                )
            f.write('</Document></kml>\n')


# ----- Module-level wrappers for interface -----
def AddNode(graph: Graph, node: Node) -> bool:
    return graph.add_node(node)

def AddSegment(graph: Graph, origin_name: str, dest_name: str) -> bool:
    return graph.add_segment(origin_name, dest_name)

def GetClosest(graph: Graph, x: float, y: float) -> Optional[Node]:
    return graph.get_closest(x, y)

def FindReachableNodes(graph: Graph, origin_name: str) -> List[Node]:
    return graph.find_reachable(origin_name)

def FindShortestPath(graph: Graph, origin_name: str, dest_name: str) -> Optional[List[Node]]:
    return graph.find_shortest_path(origin_name, dest_name)

def GetReachableSegments(graph: Graph, nodes: List[Node]) -> List[Tuple[Node, Node]]:
    s = set(nodes)
    return [(seg.origin, seg.destination) for seg in graph.segments
            if seg.origin in s and seg.destination in s]

def GetPathSegments(graph: Graph, path: List[Node]) -> List[Tuple[Node, Node]]:
    return [(path[i], path[i+1]) for i in range(len(path)-1)]


# Load graphs from files
def LoadGraphFromFile(filename: str) -> Graph:
    g = Graph()
    node_map: Dict[str, Node] = {}
    pending: List[Tuple[str, str]] = []
    mode = None
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            low = line.lower()
            if low in ('[nodos]', '[nodes]'):
                mode = 'nodes'
                continue
            if low in ('[segmentos]', '[segments]'):
                mode = 'segments'
                continue
            parts = line.split()
            if mode == 'nodes' and len(parts) >= 3:
                name, xs, ys = parts[0], parts[1], parts[2]
                try:
                    x, y = float(xs), float(ys)
                    node = Node(name, x, y)
                    g.add_node(node)
                    node_map[name] = node
                except ValueError:
                    continue
            elif mode == 'segments' and len(parts) >= 2:
                pending.append((parts[0], parts[1]))
    for o, d in pending:
        g.add_segment(o, d)
    return g


from airspace_data import AirSpace

def LoadAirspaceAsGraph(nav_file: str, seg_file: str, aer_file: Optional[str] = None) -> Graph:
    air = AirSpace()
    if aer_file:
        air.load_from_files(nav_file, seg_file, aer_file)
    else:
        air.load_from_files(nav_file, seg_file)
    g = Graph()
    id_map: Dict[int, Node] = {}
    # NavPoints
    if isinstance(air.navpoints, dict):
        for np_id, np in air.navpoints.items():
            try:
                x = float(np.longitude) * 111
                y = float(np.latitude) * 111
                node = Node(np.name, x, y)
                g.add_node(node)
                id_map[int(np.number)] = node
            except Exception:
                continue
    # Airports
    if hasattr(air, 'airports') and isinstance(air.airports, dict):
        for ap_id, ap in air.airports.items():
            try:
                x = float(ap.longitude) * 111
                y = float(ap.latitude) * 111
                name = ap.name or f"AIRPORT_{ap_id}"
                node = Node(name, x, y, is_airport=True)
                g.add_node(node)
                id_map[int(ap.number)] = node
            except Exception:
                continue
    # Segments
    for seg in getattr(air, 'navsegments', []):
        o = id_map.get(seg.origin_number)
        d = id_map.get(seg.destination_number)
        if o and d:
            g.segments.append(Segment(f"{o.name}-{d.name}", o, d))
            o.neighbors.add(d)
            d.neighbors.add(o)
    return g


# KML export for interface convenience
def ExportToKML(graph: Graph, filename: str, open_after: bool = True) -> None:
    graph.export_kml(filename)
    if open_after:
        try:
            if platform.system() == 'Windows':
                os.startfile(filename)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', filename])
            else:
                subprocess.call(['xdg-open', filename])
        except Exception:
            pass


def CalculateDistance(path: List[Node]) -> float:
    """
    Suma las distancias euclídeas entre nodos consecutivos de la ruta.
    """
    total = 0.0
    for a, b in zip(path, path[1:]):
        dx = a.x - b.x
        dy = a.y - b.y
        total += (dx*dx + dy*dy)**0.5
    return total

def EstimateFuel(distance: float, burn_rate: float = 0.2) -> float:
    """
    Estima el combustible consumido dado un burn_rate (unidades de fuel por unidad de distancia).
    Por defecto 0.2 (p.ej. 0.2 u/km).
    """
    return distance * burn_rate
