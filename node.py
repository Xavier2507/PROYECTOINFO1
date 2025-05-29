import math

# Clase Node representa un nodo del grafo con nombre, coordenadas y vecinos.
class Node:
    def __init__(self, name, x, y):
        self.name = name                  # Nombre del nodo (string)
        self.x = float(x)                 # Coordenada X (float)
        self.y = float(y)                 # Coordenada Y (float)
        self.neighbors = []              # Lista de nodos vecinos (lista de Node)

    def __str__(self):
        # Representación legible del nodo
        return f"Node({self.name}, {self.x}, {self.y})"

    def distance(self, other):
        # Devuelve la distancia euclidiana entre este nodo y otro
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx**2 + dy**2)

# Función auxiliar para añadir un vecino a un nodo
def AddNeighbor(n1, n2):
    if n2 in n1.neighbors:
        return False
    n1.neighbors.append(n2)
    return True

# Función auxiliar para calcular la distancia entre dos nodos
def Distance(n1, n2):
    dx = n1.x - n2.x
    dy = n1.y - n2.y
    return math.sqrt(dx**2 + dy**2)
