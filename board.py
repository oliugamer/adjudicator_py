from orders import Order, Move, Hold, Support, Convoy
from graph import Node

class Board:
    node_id = {}
    move_orders = []
    other_orders = []


    def __init__(self, nodes, countries):
        self.nodes = nodes
        self.countries = countries
        for idx, i in enumerate(nodes):
            self.node_id[i.name] = idx

    def getNode(self, str) -> Node:
        return self.nodes[self.node_id[str]]

    def parseOrder(self, str) -> Order:
        str = str.split(" ")
        match str[1]:
            case "":
                return
            case "m":
                order = Move(self.getNode(str[0]), self.getNode(str[2]))
                self.getNode(str[2]).recieving_move_orders.append(order)
                return order
            case "h":
                order = Hold(self.getNode(str[0]))
                return order
            case "s":
                if str[3] == "h":
                    order = Support(self.getNode(str[0]), Hold(self.getNode(str[2])))
                    # self.getNode(str[2]).recieving_orders.append(order)
                    return order
                elif str[3] == "m":
                    order = Support(self.getNode(str[0]), Move(self.getNode(str[2]), self.getNode(str[4])))
                    # self.getNode(str[2]).recieving_orders.append(order)
                    return order
                else:
                    print("Parsing Error")
            case "c":
                pass
            case _:
                print("Parsing Error")
        
    def addOrder(self, str):
        if type(self.parseOrder(str).ordering_unit) == Move:
            self.move_orders.append(self.parseOrder(str))
        else: 
            self.other_orders.append(self.parseOrder(str))

    def addRawOrder(self, order):
        if type(order) == Move:
            self.move_orders.append(self.parseOrder(str))
        else: 
            self.other_orders.append(self.parseOrder(str))

    def adjudicate(self):
        for order in self.other_orders:
            order.legal = order.ordering_unit.orderLegal(order)
            match order:
                case Hold():
                    order.ordering_unit.hold = True
                case Support():
                    order.ordering_unit.hold = True
                    if order.ordering_unit.isTapped():
                        match order.support_order:
                            case Move():
                                if order.support_order.ordering_unit.unit is not None and order.legal:
                                    if order.support_order == order.support_order.ordering_unit.unit:
                                        order.support_order.ordering_unit.unit.attacking_strength += 1
                            case Hold():
                                if order.legal:
                                    order.support_order.ordering_unit.holding_strength += 1
                    else:
                        order.fail = True
                case Convoy():
                    pass
                case _:
                    pass

        successful_moves = []
        for order in self.move_orders:
            order.legal = order.ordering_unit.orderLegal(order)
            order.ordering_unit.hold = False
            fail = False
            for i in order.ordering_unit.recieving_move_orders:
                if order.attacking_strength <= i.attacking_strength:
                    fail = True
            
            if order.attacking_strength <= order.destination.holding_strength:
                fail = True

            if not order.legal:
                fail = True

            if not fail:
                successful_moves.append(order)
                

    def __str__(self):
        for i in self.nodes:
            str(i)
        return ""

