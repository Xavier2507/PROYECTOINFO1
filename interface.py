import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
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
        tk.Button(self.root, text="Cargar Grafo", command=self.load_graph).pack()
        tk.Button(self.root, text="Mostrar Grafo", command=self.plot_graph).pack()
        tk.Button(self.root, text="Añadir Nodo", command=self.add_node).pack()
        tk.Button(self.root, text="Añadir Segmento", command=self.add_segment).pack()
        tk.Button(self.root, text="Eliminar Nodo", command=self.delete_node).pack()
        tk.Button(self.root, text="Nuevo Grafo", command=self.new_graph).pack()
        tk.Button(self.root, text="Seleccionar Nodo", command=self.select_node).pack()
        tk.Button(self.root, text="Guardar Grafo", command=self.save_graph).pack()

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
            messagebox.showwarning("", "¡No hay un grafo para mostrar!")

    def add_node(self):
        name = simpledialog.askstring("Entrada", "Ingrese el nombre del nodo:")
        x = simpledialog.askfloat("Entrada", "Ingrese la coordenada x:")
        y = simpledialog.askfloat("Entrada", "Ingrese la coordenada y:")
        if name and x is not None and y is not None:
            AddNode(self.graph, Node(name, x, y))
            messagebox.showinfo("Éxito", "¡Nodo añadido correctamente!")

    def add_segment(self):
        origin = simpledialog.askstring("Entrada", "Ingrese el nombre del nodo origen:")
        destination = simpledialog.askstring("Entrada", "Ingrese el nombre del nodo destino:")
        if origin and destination:
            if AddSegment(self.graph, origin, destination):
                messagebox.showinfo("Éxito", "¡Segmento añadido correctamente!")
            else:
                messagebox.showerror("Error", "No se pudo añadir el segmento. Verifique los nombres de los nodos.")

    def delete_node(self):
        name = simpledialog.askstring("Entrada", "Ingrese el nombre del nodo a eliminar:")
        if name:
            node = next((n for n in self.graph.nodes if n.name == name), None)
            if node:
                self.graph.nodes.remove(node)
                self.graph.segments = [s for s in self.graph.segments if s.origin != node and s.destination != node]
                messagebox.showinfo("Éxito", "¡Nodo eliminado correctamente!")
            else:
                messagebox.showerror("Error", "Nodo no encontrado.")

    def new_graph(self):
        self.graph = Graph()
        messagebox.showinfo("Éxito", "¡Nuevo grafo creado!")

    def select_node(self):
        name = simpledialog.askstring("Entrada", "Ingrese el nombre del nodo:")
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

