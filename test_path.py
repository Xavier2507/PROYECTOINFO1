from node import Node
from path import Path, AddNodeToPath, ContainsNode, CostToNode

n1 = Node("A", 0, 0)
n2 = Node("B", 3, 4)
n3 = Node("C", 6, 8)

p = Path([n1])
p = AddNodeToPath(p, n2)
p = AddNodeToPath(p, n3)

assert ContainsNode(p, n2)
assert round(p.Cost(), 2) == 10.0
assert CostToNode(p, n3) == 10.0

print("Todos los tests pasaron.")

