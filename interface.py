import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from graph import Graph, LoadGraphFromFile, Plot, PlotNode, AddNode, AddSegment
from node import Node


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Explorador de Grafos")
        self.graph = Graph()

        self.create_widgets()

    def create_widgets(self):
        btn_load = tk.Button(self.root, text="Cargar Grafo", command=self.load_graph)
        btn_load.pack()

        btn_plot = tk.Button(self.root, text="Mostrar Grafo", command=self.plot_graph)
        btn_plot.pack()

        btn_add_node = tk.Button(self.root, text="Añadir Nodo", command=self.add_node)
        btn_add_node.pack()

        btn_add_segment = tk.Button(self.root, text="Añadir Segmento", command=self.add_segment)
        btn_add_segment.pack()

        btn_select_node = tk.Button(self.root, text="Seleccionar Nodo", command=self.select_node)
        btn_select_node.pack()

        btn_save = tk.Button(self.root, text="Guardar Grafo", command=self.save_graph)
        btn_save.pack()

    def load_graph(self):
        filename = filedialog.askopenfilename(title="Seleccionar Archivo de Grafo",
                                              filetypes=[("Archivos de Texto", "*.txt")])
        if filename:
            self.graph = LoadGraphFromFile(filename)
            messagebox.showinfo("Éxito", "¡Grafo cargado correctamente!")

    def plot_graph(self):
        if self.graph.nodes:
            Plot(self.graph)
        else:
            messagebox.showwarning("Advertencia", "¡No hay un grafo para mostrar!")

    def add_node(self):
        name = tk.simpledialog.askstring("Entrada", "Ingrese el nombre del nodo:")
        x = tk.simpledialog.askfloat("Entrada", "Ingrese la coordenada x:")
        y = tk.simpledialog.askfloat("Entrada", "Ingrese la coordenada y:")
        if name and x is not None and y is not None:
            AddNode(self.graph, Node(name, x, y))

    def add_segment(self):
        origin = tk.simpledialog.askstring("Entrada", "Ingrese el nombre del nodo origen:")
        destination = tk.simpledialog.askstring("Entrada", "Ingrese el nombre del nodo destino:")
        if origin and destination:
            AddSegment(self.graph, origin, destination)

    def select_node(self):
        name = tk.simpledialog.askstring("Entrada", "Ingrese el nombre del nodo:")
        if name:
            PlotNode(self.graph, name)

    def save_graph(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de Texto", "*.txt")])
        if filename:
            with open(filename, 'w') as file:
                file.write("[Nodos]\n")
                for node in self.graph.nodes:
                    file.write(f"{node.name} {node.x} {node.y}\n")
                file.write("[Segmentos]\n")
                for segment in self.graph.segments:
                    file.write(f"{segment.origin.name} {segment.destination.name}\n")
            messagebox.showinfo("Éxito", "¡Grafo guardado correctamente!")


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
