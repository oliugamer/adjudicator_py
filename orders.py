class Order:
    def __init__(self):
        self.legal = True
        self.checked = False
        self.fail = False
        pass

    def executeOrder(self):
        pass

class Move(Order):
    def __init__(self, ordering_unit, destination, add_order=True):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.destination = destination
        self.success = False
        self.witing_on_result = False
        self.supports = []
        self.convoyed = False
        self.convoy_path = []
        self.convoy_start = None
        self.convoy_end = None
        
        if add_order:
            self.ordering_unit.unit.order = self
            self.destination.recieving_move_orders.append(self)
            self.ordering_unit.unit.attacking_strength = 1

    def executeOrder(self):
        print(self)
        unit = self.ordering_unit.movingUnit()
        if unit is None:
            return
        print("Moving unit: ", unit)
        unit.node = self.destination
        self.destination.addUnit(unit)
        # Reset
        self.supports = []
        self.convoyed = False
        self.convoy_path = []
        self.convoy_start = None
        self.convoy_end = None
    
    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.destination == self.destination

    def __str__(self):
        return self.ordering_unit.name + " m " + self.destination.name

class Retreat(Order):
    def __init__(self, ordering_unit, destination):
        super().__init__()
        self.ordering_unit = ordering_unit
        self.destination = destination
        self.ordering_unit.unit.order = self

    def executeOrder(self):
        unit = self.ordering_unit.retreatUnit()
        print("Retreating unit: ", unit)
        self.destination.addUnit(unit)
    
    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.destination == self.destination

    def __str__(self):
        return self.ordering_unit.name + " m " + self.destination.name

class Hold(Order):
    def __init__(self, ordering_unit, add_order=True):
        super().__init__()
        self.ordering_unit = ordering_unit
        if add_order:
            self.ordering_unit.unit.order = self
            self.ordering_unit.unit.attacking_strength = 0
    
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
        self.ordering_unit.unit.order = self
        self.ordering_unit.unit.attacking_strength = 0

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
        self.valid = False
        self.dislodged = False
        self.ordering_unit.unit.order = self

    def executeOrder(self):
        pass

    def __eq__(self, value):
        return self.ordering_unit == value.ordering_unit and self.move == self.move

    def __str__(self):
        return self.ordering_unit.name + " c " + str(self.move)

class Build(Order):
    def __init__(self, core, unit, coast=-1):
        super().__init__()
        self.core = core
        self.unit = unit
        self.coast = coast

    def executeOrder(self):
        if self.core.unit is not None:
            print("Invalid order")
            return
        self.core.buildUnit(self.unit, self.coast)

class Disband(Order):
    def __init__(self, disbanded_unit):
        super().__init__()
        self.disbanded_unit = disbanded_unit
        self.disbanded_unit.unit.order = self

    def executeOrder(self):
        unit = self.disbanded_unit.unit
        unit.owner.units.remove(unit)
        self.core.removeUnit()

class DisbandRetreat(Order):
    def __init__(self, disbanded_unit):
        super().__init__()
        self.disbanded_unit = disbanded_unit
        self.disbanded_unit.unit.order = self

    def executeOrder(self):
        unit = self.disbanded_unit.unit
        unit.owner.units.remove(unit)
        self.disbanded_unit.disbandRetreat()




