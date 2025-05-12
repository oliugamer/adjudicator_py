from graph import *
from units import *

class Order:
    legal = True
    checked = False
    fail = False

    def __init__(self):
        pass

    def executeOrder(self):
        pass

class Move(Order):
    def __init__(self, ordering_unit: Node, destination: Node):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.destination = destination

    def executeOrder(self):
        self.destination.unit = self.ordering_unit.unit
        self.ordering_unit.unit = None
    
    def __eq__(self, value: Move):
        return self.ordering_unit == value.ordering_unit and self.destination == self.destination

class Hold(Order):
    def __init__(self, ordering_unit: Node):
        super().__init__()
        self.ordering_unit = ordering_unit
    
    def executeOrder(self):
        pass

    def __eq__(self, value: Move):
        return self.ordering_unit == value.ordering_unit


class Support(Order):
    def __init__(self, ordering_unit: Node, support_order: Order):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.support_order = support_order

    def executeOrder(self):
        pass

    def __eq__(self, value: Move):
        return self.ordering_unit == value.ordering_unit and self.support_order == self.support_order
    

class Convoy(Order):
    def __init__(self, ordering_unit: Node, move: Move):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.move = move

    def executeOrder(self):
        pass

    def __eq__(self, value: Move):
        return self.ordering_unit == value.ordering_unit and self.move == self.move


# class Build(Order):
#     def __init__(self, node: Node, unit: Unit):
#         super().__init__()


# class Disband(Order):
#     def __init__(self, node: Node):
#         super().__init__()




