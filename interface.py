
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import matplotlib.pyplot as plt
import os
import platform
import subprocess
from typing import List, Optional
from matplotlib.collections import LineCollection

from graph import (
    Graph,
    LoadGraphFromFile,
    LoadAirspaceAsGraph,
    AddNode,
    AddSegment,
    FindReachableNodes,
    FindShortestPath,
    GetReachableSegments,
    GetPathSegments,
    GetClosest,
    CalculateDistance,
    EstimateFuel,
)
from node import Node


# ----------------------------------------
# Helper de exportación avanzado a KML
# ----------------------------------------
def ExportToKML_GUI(
        graph: Graph,
        filename: str,
        reachable: Optional[List[Node]] = None,
        path: Optional[List[Node]] = None,
        open_after: bool = True
) -> None:
    reachable = reachable or []
    path = path or []
    reachable_pairs = {(o.name, d.name) for o, d in GetReachableSegments(graph, reachable)}
    path_pairs = {(o.name, d.name) for o, d in GetPathSegments(graph, path)}

    with open(filename, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')

        # Segmentos no alcanzables (gris)
        f.write('<Folder><name>Segmentos no alcanzables</name>\n')
        for seg in graph.segments:
            key = (seg.origin.name, seg.destination.name)
            if key in reachable_pairs or key in path_pairs:
                continue
            lon1, lat1 = seg.origin.x / 111.0, seg.origin.y / 111.0
            lon2, lat2 = seg.destination.x / 111.0, seg.destination.y / 111.0
            f.write(
                f'<Placemark><name>{seg.origin.name} → {seg.destination.name}</name>'
                f'<Style><LineStyle><color>ffcccccc</color><width>1.5</width></LineStyle></Style>'
                f'<LineString><tessellate>1</tessellate>'
                f'<coordinates>{lon1},{lat1},0 {lon2},{lat2},0</coordinates>'
                '</LineString></Placemark>\n'
            )
        f.write('</Folder>\n\n')

        # Segmentos alcanzables (verde)
        if reachable_pairs:
            f.write('<Folder><name>Segmentos alcanzables</name>\n')
            for o, d in GetReachableSegments(graph, reachable):
                lon1, lat1 = o.x / 111.0, o.y / 111.0
                lon2, lat2 = d.x / 111.0, d.y / 111.0
                f.write(
                    f'<Placemark><name>{o.name} → {d.name}</name>'
                    f'<Style><LineStyle><color>ff008000</color><width>2.5</width></LineStyle></Style>'
                    f'<LineString><tessellate>1</tessellate>'
                    f'<coordinates>{lon1},{lat1},0 {lon2},{lat2},0</coordinates>'
                    '</LineString></Placemark>\n'
                )
            f.write('</Folder>\n\n')

        # Camino más corto (rojo 10m sobre terreno)
        if path_pairs:
            f.write('<Folder><name>Camino más corto</name>\n')
            coords = " ".join(f"{n.x/111.0},{n.y/111.0},10" for n in path)
            f.write(
                f'<Placemark><name>Camino más corto</name>'
                f'<Style><LineStyle><color>ff0000ff</color><width>4</width></LineStyle></Style>'
                '<LineString><tessellate>1</tessellate>'
                '<altitudeMode>relativeToGround</altitudeMode>'
                f'<coordinates>{coords}</coordinates>'
                '</LineString></Placemark>\n'
            )
            f.write('</Folder>\n\n')

        # Nodos y Aeropuertos
        f.write('<Folder><name>Nodos y Aeropuertos</name>\n')
        for node in graph.nodes:
            lon, lat = node.x / 111.0, node.y / 111.0
            if node.is_airport:
                icon = 'http://maps.google.com/mapfiles/kml/shapes/airports.png'
                label = '<LabelStyle><color>ffffffff</color><scale>2.5</scale></LabelStyle>'
                scale = 1.0
            else:
                icon = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
                label = ''
                scale = 0.6
            f.write(
                f'<Placemark><name>{node.name}</name>'
                '<Style>'
                f'<IconStyle><scale>{scale}</scale><Icon><href>{icon}</href></Icon></IconStyle>'
                f'{label}'
                '</Style>'
                f'<Point><coordinates>{lon},{lat},0</coordinates></Point>'
                '</Placemark>\n'
            )
        f.write('</Folder>\n')

        f.write('</Document>\n</kml>\n')

    if open_after:
        if platform.system() == 'Windows':
            os.startfile(filename)
        elif platform.system() == 'Darwin':
            subprocess.call(['open', filename])
        else:
            subprocess.call(['xdg-open', filename])


STYLE = {
    'bg': '#1F1F2E',
    'fg': '#E0E0E8',
    'primary': '#4E8DA7',
    'accent': '#A7C957',
    'font': ("Segoe UI", 10, "bold"),
}


class GraphApp:
    """Interfaz gráfica para Flight Planner Pro."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Flight Planner Pro")
        self.root.configure(bg=STYLE['bg'])
        self.graph = Graph()
        self.airport_names: set = set()
        self.last_origin: Optional[Node] = None
        self.last_reachable: List[Node] = []
        self.last_path: List[Node] = []
        self.selected_nodes: List[Node] = []
        self.segment_nodes: List[Node] = []
        self.fig = None
        self.ax = None
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self.root)
        style.theme_use('clam')
        style.configure('TFrame', background=STYLE['bg'])
        style.configure('TButton',
                        background=STYLE['primary'],
                        foreground=STYLE['fg'],
                        font=STYLE['font'],
                        borderwidth=0)
        style.map('TButton', background=[('active', STYLE['accent'])])

    def create_widgets(self) -> None:
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(padx=20, pady=20, fill='x')

        title = ttk.Label(
            frame, text="✈️ Flight Planner Pro",
            font=("Segoe UI", 16, "bold"),
            background=STYLE['bg'],
            foreground=STYLE['accent']
        )
        title.pack(pady=(0, 15))

        opciones = [
            ("Cargar Grafo", self.load_graph),
            ("Mostrar Grafo", self.plot_graph),
            ("Añadir Nodo", self.add_node),
            ("Eliminar Nodo", self.delete_node),
            ("Nuevo Grafo", self.new_graph),
            ("Guardar Grafo", self.save_graph),
            ("Exportar KML", self.export_kml),
            ("Ruta Multi-Etapa", self.multi_stage_route),
        ]
        for text, cmd in opciones:
            btn = ttk.Button(frame, text=text, command=cmd, style='TButton')
            btn.pack(fill='x', pady=5)

    def load_graph(self) -> None:
        try:
            use_air = messagebox.askyesno("Tipo de grafo",
                                          "¿Cargar mapa aéreo? (3 archivos)")
            if use_air:
                nav = filedialog.askopenfilename(title="NAV",
                                                 filetypes=[("TXT", "*.txt")])
                seg = filedialog.askopenfilename(title="SEG",
                                                 filetypes=[("TXT", "*.txt")])
                aer = filedialog.askopenfilename(title="AER",
                                                 filetypes=[("TXT", "*.txt")])
                if nav and seg and aer:
                    self.graph = LoadAirspaceAsGraph(nav, seg, aer)
                    with open(aer, encoding='utf-8') as fa:
                        for line in fa:
                            code = line.strip()
                            if code:
                                self.airport_names.add(code)
                    for n in self.graph.nodes:
                        n.is_airport = (n.name in self.airport_names)
            else:
                path = filedialog.askopenfilename(title="Grafo",
                                                  filetypes=[("TXT", "*.txt")])
                if path:
                    self.graph = LoadGraphFromFile(path)

            messagebox.showinfo("Éxito",
                                f"{len(self.graph.nodes)} nodos cargados")
            if self.fig:
                self.draw_base_graph()
                self.fig.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_graph(self) -> None:
        if not self.graph.nodes:
            messagebox.showwarning("Sin grafo", "Carga primero un grafo.")
            return
        self.selected_nodes.clear()
        self.segment_nodes.clear()
        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig, self.ax = plt.subplots()
            self.fig.canvas.mpl_connect('button_press_event', self.onclick)
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.draw_base_graph()
        plt.show(block=False)

    def draw_base_graph(self) -> None:
        self.ax.clear()
        lines = [((s.origin.x, s.origin.y),
                  (s.destination.x, s.destination.y))
                 for s in self.graph.segments]
        self.ax.add_collection(LineCollection(lines, colors='gray',
                                              linewidths=1, alpha=0.5,
                                              zorder=1))
        xs = [n.x for n in self.graph.nodes]
        ys = [n.y for n in self.graph.nodes]
        self.ax.scatter(xs, ys, c='black', s=30, zorder=2)
        for n in self.graph.nodes:
            color = 'yellow' if n.is_airport else 'black'
            size = 8 if n.is_airport else 6
            weight = 'bold' if n.is_airport else 'normal'
            self.ax.text(n.x + 0.1, n.y + 0.1, n.name,
                         fontsize=size, color=color,
                         weight=weight, zorder=3)
        self.ax.set_title("Grafo Interactivo")
        self.ax.axis('equal')

    def onclick(self, event) -> None:
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        node = self.get_closest_node(event.xdata, event.ydata)
        if not node:
            return
        if event.button == 1:
            self.selected_nodes.append(node)
            if len(self.selected_nodes) == 1:
                self.last_origin = node
                self.last_reachable = FindReachableNodes(self.graph, node.name)
                self.last_path = []
                self.highlight_reachable(node)
            else:
                path = FindShortestPath(self.graph,
                                        self.selected_nodes[0].name,
                                        node.name)
                if path:
                    self.last_path = path
                    self.highlight_reachable_path(path)
                self.selected_nodes.clear()
        elif event.button == 3:
            self.segment_nodes.append(node)
            if len(self.segment_nodes) == 2:
                AddSegment(self.graph,
                           self.segment_nodes[0].name,
                           self.segment_nodes[1].name)
                self.segment_nodes.clear()
                self.draw_base_graph()
        self.fig.canvas.draw()

    def on_motion(self, event) -> None:
        if hasattr(self, 'dragging_node') and self.dragging_node and event.inaxes == self.ax:
            # omitido manejo drag para brevedad
            pass

    def on_release(self, event) -> None:
        self.dragging_node = None

    def get_closest_node(self, x: float, y: float) -> Optional[Node]:
        return GetClosest(self.graph, x, y)

    def highlight_reachable(self, origin: Node) -> None:
        self.draw_base_graph()
        self.ax.scatter([origin.x], [origin.y],
                        c='blue', s=50, zorder=5)
        segs = GetReachableSegments(self.graph, self.last_reachable)
        lines = [((o.x, o.y), (d.x, d.y)) for o, d in segs]
        self.ax.add_collection(LineCollection(lines,
                                              colors='#008000',
                                              linewidths=2,
                                              zorder=4))
        self.ax.set_title(f"Alcanzables desde {origin.name}")

    def highlight_reachable_path(self, path: List[Node]) -> None:
        segs = GetPathSegments(self.graph, path)
        lines = [((o.x, o.y), (d.x, d.y)) for o, d in segs]
        self.ax.add_collection(LineCollection(lines,
                                              colors='red',
                                              linewidths=3,
                                              zorder=10))
        self.ax.set_title(f"Camino: {' → '.join(n.name for n in path)}")

    def add_node(self) -> None:
        name = simpledialog.askstring("Nombre", "Ingrese el nombre del nodo:")
        x = simpledialog.askfloat("X", "Ingrese la coordenada x:")
        y = simpledialog.askfloat("Y", "Ingrese la coordenada y:")
        if name and x is not None and y is not None:
            AddNode(self.graph, Node(name, x, y))
            self.draw_base_graph()
            self.fig.canvas.draw()

    def delete_node(self) -> None:
        name = simpledialog.askstring("Eliminar nodo", "Nombre del nodo a eliminar:")
        node = next((n for n in self.graph.nodes if n.name == name), None)
        if node:
            self.graph._nodes.pop(node.name, None)
            self.graph.segments = [
                s for s in self.graph.segments
                if s.origin != node and s.destination != node
            ]
            self.draw_base_graph()
            self.fig.canvas.draw()

    def new_graph(self) -> None:
        self.graph = Graph()
        self.draw_base_graph()
        self.fig.canvas.draw()

    def save_graph(self) -> None:
        fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                          filetypes=[("TXT", "*.txt")])
        if fn:
            with open(fn, 'w', encoding='utf-8') as f:
                f.write("[Nodos]\n")
                for n in self.graph.nodes:
                    f.write(f"{n.name} {n.x} {n.y}\n")
                f.write("[Segmentos]\n")
                for s in self.graph.segments:
                    f.write(f"{s.origin.name} {s.destination.name}\n")
            messagebox.showinfo("Guardado", "¡Grafo guardado correctamente!")

    def export_kml(self) -> None:
        if not self.last_reachable and self.graph.nodes:
            self.last_origin = self.graph.nodes[0]
            self.last_reachable = FindReachableNodes(self.graph, self.last_origin.name)
        fn = filedialog.asksaveasfilename(defaultextension=".kml",
                                          filetypes=[("KML files", "*.kml")])
        if not fn:
            return
        try:
            ExportToKML_GUI(
                self.graph,
                fn,
                reachable=self.last_reachable,
                path=self.last_path,
                open_after=True
            )
            messagebox.showinfo("Exportación KML", f"Guardado en: {fn}")
        except Exception as e:
            messagebox.showerror("Error KML", f"No se pudo exportar:\n{e}")

    def multi_stage_route(self) -> None:
        text = simpledialog.askstring(
            "Ruta Multi-Etapa",
            "Introduce waypoints separados por comas (p.ej: A,B,C,D):"
        )
        if not text:
            return

        names = [s.strip() for s in text.split(",") if s.strip()]
        if len(names) < 2:
            messagebox.showwarning("Atención", "Necesitas al menos 2 nodos.")
            return

        full_path: List[Node] = []
        for src, dst in zip(names, names[1:]):
            leg = FindShortestPath(self.graph, src, dst)
            if not leg:
                messagebox.showerror("Error", f"No hay ruta entre {src} → {dst}")
                return
            if full_path and leg[0] == full_path[-1]:
                full_path.extend(leg[1:])
            else:
                full_path.extend(leg)

        total_dist = CalculateDistance(full_path)
        fuel = EstimateFuel(total_dist)

        messagebox.showinfo(
            "Ruta Multi-Etapa",
            (f"Waypoints: {' → '.join(names)}\n"
             f"Distancia total: {total_dist:.2f} km\n"
             f"Combustible estimado: {fuel:.2f} l")
        )

        self.last_path = full_path
        if self.fig:
            self.draw_base_graph()
            self.highlight_reachable_path(full_path)
            self.fig.canvas.draw()


# Entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
