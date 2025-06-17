from orders import Order, Move, Hold, Support, Convoy
from units import Unit, Fleet, Army
from graph import Node, InlandTile, CoastTile, SeaTile, MultipleCoastTile
from country import Country
from board import Board
from metrics import Metrics
from heuristics import CompleteH1, CompleteH2, LookAhead


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

    n1.addArmyAdjacencies([n2, n3, n4])
    n2.addArmyAdjacencies([n1, n7, n3])
    n3.addArmyAdjacencies([n1, n2, n4, n5])
    n4.addArmyAdjacencies([n1, n3])
    n4.addFleetAdjacencies([n10, n11])
    n5.addArmyAdjacencies([n3])
    n5.addFleetAdjacencies([n9, n10])
    n6.addArmyAdjacencies([n7])
    n6.addFleetAdjacencies([n7, n8, n9])
    n7.addArmyAdjacencies([n2, n6])
    n7.addFleetAdjacencies([n6, n8, n9])
    n8.addFleetAdjacencies([n5, n7, n9])
    n9.addFleetAdjacencies([n5, n6, n7, n8, n10])
    n10.addFleetAdjacencies([n4, n5, n9, n11])
    n11.addFleetAdjacencies([n4, n10])

    c1 = Country("c1")
    c2 = Country("c2")

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


def getOrders(board: Board):
    print(board.year, board.phase)
    while True:
        order = input("Order: ")

        if order == "exit" or order == "":
            break
    
        if order == "i":
            print("Info")
            p = input("Province: ")
            print(board.getNode(p))
            continue

        if order == "v":
            board.printGraph()
            continue

        if order == "h":
            c = CompleteH1(board)
            c2 = CompleteH2(board)
            for i in board.countries:
                print(i.name, c.evaluatePosition(i), c2.evaluatePosition(i))
            continue

        if order == "s":
            c = LookAhead(board)
            scores = []
            for i in board.countries:
                scores.append((i.name, c.evaluatePosition(i)))
            print(scores)
            continue

        board.addOrder(order)
    
    board.printOrders()


board = Board.createBoardFromFile("initialmap.txt")
board.importBoardState("units.txt")
print(board)
while True:
    getOrders(board)

    board.adjudicate()

    print(board, end="")

    exit = input("Exit? ")
    
    if exit == "yes":
        break

