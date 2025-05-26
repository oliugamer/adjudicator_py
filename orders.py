class Order:
    def __init__(self):
        self.legal = True
        self.checked = False
        self.fail = False
        pass

    def executeOrder(self):
        pass

class Move(Order):
    def __init__(self, ordering_unit, destination):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.destination = destination
        self.success = False

    def executeOrder(self):
        unit = self.ordering_unit.movingUnit()
        print("Moving unit: ", unit)
        self.destination.addUnit(unit)
    
    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.destination == self.destination

    def __str__(self):
        return self.ordering_unit.name + " m " + self.destination.name

class Retreat(Order):
    def __init__(self, ordering_unit, destination):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.destination = destination

    def executeOrder(self):
        unit = self.ordering_unit.retreatUnit()
        print("Retreating unit: ", unit)
        self.destination.addUnit(unit)
    
    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.destination == self.destination

    def __str__(self):
        return self.ordering_unit.name + " m " + self.destination.name

class Hold(Order):
    def __init__(self, ordering_unit):
        super().__init__()
        self.ordering_unit = ordering_unit
    
    def executeOrder(self):
        pass

    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit

    def __str__(self):
        return self.ordering_unit.name + " h"

class Support(Order):
    def __init__(self, ordering_unit, support_order: Order):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.support_order = support_order
        self.tapped = False
        self.dislodged = False

    def executeOrder(self):
        pass

    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.support_order == self.support_order
    
    def __str__(self):
        return self.ordering_unit.name + " s " + str(self.support_order)
    
class Convoy(Order):
    def __init__(self, ordering_unit, move: Move):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.move = move
        self.convoy_path = []
        self.dislodged = []

    def executeOrder(self):
        pass

    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.move == self.move

class Build(Order):
    def __init__(self, core, unit):
        super().__init__()
        self.core = core
        self.unit = unit

    def executeOrder(self):
        if self.core.unit is not None:
            print("Invalid order")
            return
        self.core.addUnit(self.unit)

class Disband(Order):
    def __init__(self, disbanded_unit):
        super().__init__()
        self.disbanded_unit = disbanded_unit

    def executeOrder(self):
        self.core.removeUnit()

class DisbandRetreat(Order):
    def __init__(self, disbanded_unit):
        super().__init__()
        self.disbanded_unit = disbanded_unit

    def executeOrder(self):
        self.core.disbandRetreat()




