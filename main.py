from orders import *
from units import *
from graph import * 
from country import *
from board import *


def createTestBoard():
    n1 = InlandTile("n1", [], (1, 0), True, None, None)
    n2 = InlandTile("n2", [], (2, 0), True, None, None)
    n3 = InlandTile("n3", [], (3, 0), False, None, None)
    n4 = CoastTile("n4", [], (4, 0), True, None, None)
    n5 = CoastTile("n5", [], (5, 0), True, None, None)
    n6 = CoastTile("n6", [], (1, 1), False, None, None)
    n7 = CoastTile("n7", [], (1, 2), True, None, None)
    n8 = SeaTile("n8", [], (1, 3), False, None, None)
    n9 = SeaTile("n9", [], (1, 4), False, None, None)
    n10 = SeaTile("n10", [], (2, 3), False, None, None)
    n11 = SeaTile("n11", [], (3, 4), False, None, None)

    c1 = Country("c1")
    c2 = Country("c1")

    c1.addProvince(n1)
    c1.addProvince(n2)
    c1.addProvince(n3)
    c1.addProvince(n7)
    c2.addProvince(n4)
    c2.addProvince(n5)
    c2.addProvince(n6)

    c1.addCore(n1)
    c1.addCore(n2)
    c1.addCore(n7)
    c2.addCore(n4)
    c2.addCore(n5)

    nodes = [n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11]
    
    board = Board(nodes, [c1, c2])

    u1 = Army(n1, c1)
    u2 = Army(n2, c1)
    u3 = Fleet(n7, c1)
    u4 = Army(n4, c2)
    u5 = Fleet(n5, c2)

    return board




board = createTestBoard()
print(board)
while True:
    order = input("Order: ")

    if order == "exit" or order == "":
        break

    order = board.parseOrder(order)

    order.executeOrder()

    print(board, end="")