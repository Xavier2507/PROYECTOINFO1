import tkinter as tk
from tkinter.filedialog import askopenfilename
from graph import LoadGraphFromFile, Plot, PlotNode
from example_graph import create_example_graph, create_custom_graph

g = None

def cargar(f):
    global g
    if callable(f):
        g = f()
    else:
        g = LoadGraphFromFile(f)
    Plot(g)

def vecinos():
    if g:
        nombre = entrada.get().strip()
        print(f"Buscando vecinos de: {nombre}")
        ok = PlotNode(g, nombre)
        if not ok:
            print("Nodo no encontrado.")


ventana = tk.Tk()
ventana.title("Grafo")

tk.Button(ventana, text="Mostrar ejemplo", command=lambda: cargar(create_example_graph)).pack()
tk.Button(ventana, text="Mostrar inventado", command=lambda: cargar(create_custom_graph)).pack()
tk.Button(ventana, text="Cargar desde archivo", command=lambda: cargar(askopenfilename())).pack()

entrada = tk.Entry(ventana)
entrada.pack()

tk.Button(ventana, text="Mostrar vecinos", command=vecinos).pack()

ventana.mainloop()
