import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
from graph import Graph, LoadGraphFromFile, LoadAirspaceAsGraph, AddNode, AddSegment, FindReachableNodes, FindShortestPath
from node import Node

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Grafos")
        self.graph = Graph()
        self.selected_nodes = []
        self.segment_nodes = []
        self.dragging_node = None
        self.fig = None
        self.ax = None
        self.create_widgets()

    def create_widgets(self):
        tk.Button(self.root, text="Cargar Grafo", command=self.load_graph).pack()
        tk.Button(self.root, text="Mostrar Grafo Interactivo", command=self.plot_graph).pack()
        tk.Button(self.root, text="Añadir Nodo", command=self.add_node).pack()
        tk.Button(self.root, text="Eliminar Nodo", command=self.delete_node).pack()
        tk.Button(self.root, text="Nuevo Grafo", command=self.new_graph).pack()
        tk.Button(self.root, text="Guardar Grafo", command=self.save_graph).pack()

    def load_graph(self):
        use_airspace = messagebox.askyesno("Tipo de grafo", "¿Desea cargar un mapa aéreo (requiere 3 archivos)?")
        try:
            if use_airspace:
                nav_file = filedialog.askopenfilename(title="Seleccionar archivo NAV", filetypes=[("Archivos de texto", "*.txt")])
                if not nav_file: return
                seg_file = filedialog.askopenfilename(title="Seleccionar archivo SEG", filetypes=[("Archivos de texto", "*.txt")])
                if not seg_file: return
                aer_file = filedialog.askopenfilename(title="Seleccionar archivo AER", filetypes=[("Archivos de texto", "*.txt")])
                if not aer_file: return
                self.graph = LoadAirspaceAsGraph(str(nav_file), str(seg_file), str(aer_file))
                messagebox.showinfo("Éxito", f"Mapa aéreo cargado: {len(self.graph.nodes)} nodos")
            else:
                file = filedialog.askopenfilename(title="Seleccionar grafo", filetypes=[("Archivos de texto", "*.txt")])
                if file:
                    self.graph = LoadGraphFromFile(str(file))
                    messagebox.showinfo("Éxito", f"Grafo cargado: {len(self.graph.nodes)} nodos")
            if self.fig and self.ax:
                self.draw_base_graph(self.ax)
                self.fig.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el grafo:\n{e}")

    def plot_graph(self):
        if not self.graph.nodes:
            messagebox.showwarning("Advertencia", "¡No hay un grafo para mostrar!")
            return

        self.selected_nodes.clear()
        self.segment_nodes.clear()

        if self.fig is None or not plt.fignum_exists(self.fig.number):
            self.fig, self.ax = plt.subplots()
            self.fig.canvas.mpl_connect('button_press_event', self.onclick)
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
            self.fig.canvas.mpl_connect('button_release_event', self.on_release)

        self.draw_base_graph(self.ax)
        self.fig.canvas.draw()
        plt.show(block=False)

    def onclick(self, event):
        if event.inaxes != self.ax:
            return
        clicked_node = self.get_closest_node(event.xdata, event.ydata)
        if not clicked_node:
            return
        if event.button == 1:
            self.dragging_node = clicked_node
            self.selected_nodes.append(clicked_node)
            if len(self.selected_nodes) == 1:
                self.highlight_reachable(self.ax, clicked_node)
            elif len(self.selected_nodes) == 2:
                path = FindShortestPath(self.graph, self.selected_nodes[0].name, self.selected_nodes[1].name)
                if path:
                    self.highlight_path(self.ax, path)
                self.selected_nodes.clear()
            self.fig.canvas.draw()
        elif event.button == 3:
            self.segment_nodes.append(clicked_node)
            if len(self.segment_nodes) == 2:
                o, d = self.segment_nodes
                if AddSegment(self.graph, o.name, d.name):
                    messagebox.showinfo("Segmento creado", f"{o.name} → {d.name}")
                    self.draw_base_graph(self.ax)
                else:
                    messagebox.showwarning("Error", "No se pudo añadir el segmento.")
                self.segment_nodes.clear()
                self.fig.canvas.draw()

    def on_motion(self, event):
        if self.dragging_node and event.inaxes == self.ax:
            self.dragging_node.x = event.xdata
            self.dragging_node.y = event.ydata
            self.draw_base_graph(self.ax)
            self.fig.canvas.draw()

    def on_release(self, event):
        self.dragging_node = None

    def draw_base_graph(self, ax):
        ax.clear()
        for s in self.graph.segments:
            ax.annotate('', xy=(s.destination.x, s.destination.y),
                        xytext=(s.origin.x, s.origin.y),
                        arrowprops=dict(arrowstyle="->", color='black', lw=1, alpha=0.5))
        for n in self.graph.nodes:
            ax.plot(n.x, n.y, 'o', color='black')
            ax.text(n.x + 0.1, n.y + 0.1, n.name, fontsize=8)
        ax.set_title("Grafo Interactivo")
        ax.axis('equal')

    def get_closest_node(self, x, y, threshold=1.0):
        return min(
            (n for n in self.graph.nodes),
            key=lambda n: ((n.x - x) ** 2 + (n.y - y) ** 2) ** 0.5,
            default=None
        )

    def highlight_reachable(self, ax, origin):
        reachable = FindReachableNodes(self.graph, origin.name)
        for s in self.graph.segments:
            if s.origin == origin and s.destination in reachable:
                ax.annotate('', xy=(s.destination.x, s.destination.y), xytext=(s.origin.x, s.origin.y),
                            arrowprops=dict(arrowstyle="->", color='green', lw=2))
            else:
                ax.annotate('', xy=(s.destination.x, s.destination.y), xytext=(s.origin.x, s.origin.y),
                            arrowprops=dict(arrowstyle="->", color='gray', lw=0.5, alpha=0.3))
        for n in self.graph.nodes:
            color = 'blue' if n == origin else 'green' if n in reachable else 'lightgray'
            ax.plot(n.x, n.y, 'o', color=color)
            ax.text(n.x + 0.1, n.y + 0.1, n.name, fontsize=8)

    def highlight_path(self, ax, path):
        for i in range(len(path.nodes) - 1):
            n1 = path.nodes[i]
            n2 = path.nodes[i + 1]
            ax.plot([n1.x, n2.x], [n1.y, n2.y], 'r-', linewidth=3, zorder=10)

    def add_node(self):
        name = simpledialog.askstring("Nombre", "Ingrese el nombre del nodo:")
        x = simpledialog.askfloat("X", "Ingrese la coordenada x:")
        y = simpledialog.askfloat("Y", "Ingrese la coordenada y:")
        if name and x is not None and y is not None:
            if AddNode(self.graph, Node(name, x, y)):
                if self.ax:
                    self.draw_base_graph(self.ax)
                    self.fig.canvas.draw()
                messagebox.showinfo("Éxito", "Nodo añadido correctamente.")
            else:
                messagebox.showwarning("Repetido", "Ese nodo ya existe.")

    def delete_node(self):
        name = simpledialog.askstring("Eliminar nodo", "Nombre del nodo a eliminar:")
        node = next((n for n in self.graph.nodes if n.name == name), None)
        if node:
            self.graph.nodes.remove(node)
            self.graph.segments = [s for s in self.graph.segments if s.origin != node and s.destination != node]
            if self.ax:
                self.draw_base_graph(self.ax)
                self.fig.canvas.draw()
            messagebox.showinfo("Hecho", "Nodo eliminado.")
        else:
            messagebox.showerror("Error", "Nodo no encontrado.")

    def new_graph(self):
        self.graph = Graph()
        if self.ax:
            self.ax.clear()
            self.fig.canvas.draw()
        messagebox.showinfo("Nuevo", "Grafo vacío creado.")

    def save_graph(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de Texto", "*.txt")])
        if filename:
            with open(filename, 'w') as file:
                file.write("[Nodos]\n")
                for n in self.graph.nodes:
                    file.write(f"{n.name} {n.x} {n.y}\n")
                file.write("[Segmentos]\n")
                for s in self.graph.segments:
                    file.write(f"{s.origin.name} {s.destination.name}\n")
            messagebox.showinfo("Guardado", "¡Grafo guardado correctamente!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
