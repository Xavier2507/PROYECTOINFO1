from node import *

# Crear dos nodos con nombre y coordenadas
n1 = Node('aaa', 0, 0)
n2 = Node('bbb', 3, 4)

# Probar la función Distance: debe imprimir 5.0 (teorema de Pitágoras)
print(Distance(n1, n2))  # → 5.0

# Añadir n2 como vecino de n1: primera vez debe devolver True
print(AddNeighbor(n1, n2))  # → True

# Intentar añadir de nuevo el mismo vecino: debe devolver False
print(AddNeighbor(n1, n2))  # → False

# Mostrar el diccionario interno del nodo n1 para ver sus atributos
print(n1.__dict__)

# Imprimir los atributos de cada vecino del nodo n1
for n in n1.neighbors:
    print(n.__dict__)
