from orders import Order, Move, Hold, Support, Convoy
from units import Army, Fleet

class Node:
    dislodged_unit = None
    recieving_move_orders = []
    holding_strength = 0
    hold = False
    unit = None

    def __init__(self, name, alias, node_placement, is_sc, cored_by, owned_by):
        self.name = name
        self.alias = alias
        self.node_placement = node_placement
        self.is_sc = is_sc
        self.cored_by = cored_by
        self.owned_by = owned_by

    def addUnit(self, unit):
        self.unit = unit
        self.holding_strength = 1

    def removeUnit(self):
        self.unit = None
        self.holding_strength = 0

    def orderLegal(self, order):
        pass

    def isTapped(self):
        for i in self.recieving_move_orders:
            if i.ordering_unit.orderLegal(i):
                return True
        return False

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        print(">"*10)
        print("NAME -", self.name)
        for j in self.alias:
            print(j, end=", ")
        print("-"*10)
        print(f"Sc - {self.is_sc}")
        print(f"Owned by - {str(self.owned_by)}")
        print(f"Cored by - {str(self.cored_by)}")
        print(f"Unit - {str(self.unit)}")
        print("<"*10)
        print()
        return ""

    
class InlandTile(Node):
    army_adjacencies = []

    def __init__(self, name, alias, node_placement, is_sc, cored_by, owned_by):
        super().__init__(name, alias, node_placement, is_sc, cored_by, owned_by)

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)

    def getArmyAdjacencies(self):
        return self.army_adjacencies

    def orderLegal(self, order: Order):
        match order:
            case Move():
                if order.destination in self.getArmyAdjacencies():
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getArmyAdjacencies():
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getArmyAdjacencies():
                            return True
                        return False
                return False
            case _:
                return False

class SeaTile(Node):
    fleet_adjacencies = []

    def __init__(self, name, alias, node_placement, is_sc, cored_by, owned_by):
        super().__init__(name, alias, node_placement, is_sc, cored_by, owned_by)

    def addFleetAdjacency(self, node):
        self.fleet_adjacencies.append(node)
    
    def getFleetAdjacencies(self):
        return self.fleet_adjacencies

    def orderLegal(self, order: Order):
        match order:
            case Move():
                if order.destination in self.getFleetAdjacencies():
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getFleetAdjacencies():
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getFleetAdjacencies():
                            return True
                        return False
                return False
            case Convoy():
                pass
            case _:
                return False


class Coast:
    fleet_adjacencies = []

    def __init__(self):
        pass


class CoastTile(Node):
    army_adjacencies = []

    def __init__(self, name, alias, node_placement, is_sc, cored_by, owned_by):
        super().__init__(name, alias, node_placement, is_sc, cored_by, owned_by)
        self.coast = Coast()

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)

    def addFleetAdjacency(self, node):
        self.coast.fleet_adjacencies.append(node)
    
    def getArmyAdjacencies(self):
        return self.army_adjacencies

    def getFleetAdjacencies(self):
        return self.coast.fleet_adjacencies
    
    def orderLegalArmy(self, order: Order):
        match order:
            case Move():
                if order.destination in self.getArmyAdjacencies():
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getArmyAdjacencies():
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getArmyAdjacencies():
                            return True
                        return False
                return False
            case _:
                return False

    def orderLegalFleet(self, order: Order):
        match order:
            case Move():
                if order.destination in self.getFleetAdjacencies():
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getFleetAdjacencies():
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getFleetAdjacencies():
                            return True
                        return False
                return False
            case Convoy():
                pass
            case _:
                return False
            
    def orderLegal(self, order: Order):
        match order.ordering_unit.unit:
            case Army():
                return self.orderLegalArmy(order)
            case Fleet():
                return self.orderLegalFleet(order)
            case _:
                return False

class MultipleCoastTile(Node):
    army_adjacencies = []
    coasts = [None, None, None, None]
    unit_coast = -1

    def __init__(self, name, alias, node_placement, is_sc, cored_by, owned_by, nc = False, sc = False, ec = False, wc = False):
        super().__init__(name, alias, node_placement, is_sc, cored_by, owned_by)
        if nc:
            self.coasts[0] = Coast()
        if sc:
            self.coasts[1] = Coast()
        if ec:
            self.coasts[2] = Coast()
        if wc:
            self.coasts[3] = Coast()

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)

    def addFleetAdjacencies(self, node, nc = False, sc = False, ec = False, wc = False):
        try: 
            if nc:
                self.coasts[0].fleet_adjacencies.append(node)
            elif sc:
                self.coasts[1].fleet_adjacencies.append(node)
            elif ec:
                self.coasts[2].fleet_adjacencies.append(node)
            elif wc:
                self.coasts[3].fleet_adjacencies.append(node)
        except:
            pass

    def getArmyAdjacencies(self):
            return self.army_adjacencies

    def getFleetAdjacencies(self, nc = False, sc = False, ec = False, wc = False):
        try: 
            if nc:
                return self.coasts[0].fleet_adjacencies
            elif sc:
                return self.coasts[1].fleet_adjacencies
            elif ec:
                return self.coasts[2].fleet_adjacencies
            elif wc:
                return self.coasts[3].fleet_adjacencies
        except:
            return []
        return []

    def orderLegalArmy(self, order: Order):
        match order:
            case Move():
                if order.destination in self.getArmyAdjacencies():
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getArmyAdjacencies():
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getArmyAdjacencies():
                            return True
                        return False
                return False
            case _:
                return False

    def orderLegalFleet(self, order: Order):
        nc, sc, ec, wc = self.unit_coast == 0, self.unit_coast == 1, self.unit_coast == 2, self.unit_coast == 3
        match order:
            case Move():
                if order.destination in self.getFleetAdjacencies(nc, sc, ec, wc):
                    return True
                return False
            case Hold():
                return True
            case Support():
                match order.support_order:
                    case Move():
                        if order.support_order.destination in self.getFleetAdjacencies(nc, sc, ec, wc):
                            return True
                        return False
                    case Hold():
                        if order.support_order.ordering_unit in self.getFleetAdjacencies(nc, sc, ec, wc):
                            return True
                        return False
                return False
            case Convoy():
                pass
            case _:
                return False

    def orderLegal(self, order: Order):
        match order.ordering_unit.unit:
            case Army():
                return self.orderLegalArmy(order)
            case Fleet():
                return self.orderLegalFleet(order)
            case _:
                return False

    def addUnit(self, unit, coast = -1):
        self.unit_coast = coast
        self.unit = unit
        self.holding_strength = 1

    def removeUnit(self):
        self.unit_coast = -1
        self.unit = None
        self.holding_strength = 0

