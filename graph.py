from orders import Order, Move, Hold, Support, Convoy
import units

class Node:
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        self.name = name
        self.alias = alias
        self.node_placement = node_placement
        self.core = core
        self.cored_by = cored_by
        self.owned_by = owned_by
        self.dislodged_unit = None
        self.moving_unit = None
        self.recieving_move_orders = []
        self.holding_strength = 0
        self.hold = False
        self.unit = None
        self.militarized = False
        self.valid_retreats = []

    def addUnit(self, unit):
        print("Adding unit", self.name, unit)
        if self.unit is not None:
            self.dislodgeUnit()
        self.unit = unit
        self.holding_strength = 1

    def dislodgeUnit(self):
        print("Dislodging...")
        self.dislodged_unit = self.getUnit()
        self.removeUnit()

    def removeUnit(self):
        self.unit = None
        self.holding_strength = 0

    def movingUnit(self):
        aux = self.moving_unit
        self.moving_unit = None
        return aux
    
    def retreatUnit(self):
        aux = self.dislodged_unit
        self.dislodged_unit = None
        return aux
    
    def disbandRetreat(self):
        self.dislodged_unit = None

    def orderLegal(self, order):
        pass

    def isTapped(self):
        # TODO Add dislodged convoy not tapping
        for i in self.recieving_move_orders:
            if i.ordering_unit.orderLegal(i):
                if type(self.unit.order.support_order) == Move and i.ordering_unit != self.unit.order.support_order.destination:
                    return True
        return False
    
    def getUnit(self):
        return self.unit

    def moveUnit(self):
        print("Preparing unit...")
        self.moving_unit = self.getUnit()
        self.removeUnit()

    def resetAfterAdju(self):
        if self.unit is not None:
            self.holding_strength = 1
        else:
            self.holding_strength = 0
        self.hold = False
        self.militarized = False
        self.recieving_move_orders = []

    def resetRetreats(self):
        self.valid_retreats = []

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        print(">"*10)
        print("NAME -", self.name)
        for j in self.alias:
            print(j, end=", ")
        print("-"*10)
        print(f"Sc - {self.core}")
        print(f"Owned by - {str(self.owned_by)}")
        print(f"Cored by - {str(self.cored_by)}")
        print(f"Unit - {str(self.unit)}")
        print(f"Dislodged Unit - {str(self.dislodged_unit)}")
        print("<"*10)
        print()
        return ""


class InlandTile(Node):
    army_adjacencies = []

    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)
    
    def addArmyAdjacencies(self, nodes):
        for i in nodes:
            self.addArmyAdjacency(i)

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
    
    def dislodgeUnit(self):
        for i in self.getArmyAdjacencies():
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)
        return super().dislodgeUnit()

class SeaTile(Node):
    fleet_adjacencies = []

    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)

    def addFleetAdjacency(self, node):
        self.fleet_adjacencies.append(node)
    
    def addFleetAdjacencies(self, nodes):
        for i in nodes:
            self.addFleetAdjacency(i)
    
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
                # TODO
                # if type(order.ordering_unit) != SeaTile():
                #     return False
                # adjacencies = self.getFleetAdjacencies()
                # if order.move.ordering_unit in adjacencies:
                #     order.move.ordering_unit.convoy_path.append(order)
                #     return True
                # if order.move.destination in adjacencies:
                #     return True
                # for i in adjacencies:
                #     if i.unit.order == 
                return False
            case _:
                print("Not an order ._.")
                return False

    def dislodgeUnit(self):
        for i in self.getFleetAdjacencies():
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)
        return super().dislodgeUnit()

class Coast:
    fleet_adjacencies = []

    def __init__(self):
        pass


class CoastTile(Node):
    army_adjacencies = []

    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)
        self.coast = Coast()

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)

    def addArmyAdjacencies(self, nodes):
        for i in nodes:
            self.addArmyAdjacency(i)
    
    def addFleetAdjacency(self, node):
        self.coast.fleet_adjacencies.append(node)
    
    def addFleetAdjacencies(self, nodes):
        for i in nodes:
            self.addFleetAdjacency(i)
    
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
            case _:
                return False
            
    def orderLegal(self, order: Order):
        match order.ordering_unit.unit:
            case units.Army():
                return self.orderLegalArmy(order)
            case units.Fleet():
                return self.orderLegalFleet(order)
            case _:
                return False
            
    def getArmyRetreats(self):
        for i in self.getArmyAdjacencies():
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)
    
    def getFleetRetreats(self):
        for i in self.getFleetAdjacencies():
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)

    def dislodgeUnit(self):
        match self.unit:
            case units.Army():
                self.getArmyAdjacencies()
            case units.Fleet():
                self.getFleetAdjacencies()
        return super().dislodgeUnit()

class MultipleCoastTile(Node):
    army_adjacencies = []
    coasts = [None, None, None, None]
    unit_coast = -1

    def __init__(self, name, alias, node_placement, core, cored_by, owned_by, nc = False, sc = False, ec = False, wc = False):
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)
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

    def addArmyAdjacencies(self, nodes):
        for i in nodes:
            self.addArmyAdjacency(i)

    def addFleetAdjacency(self, node, nc = False, sc = False, ec = False, wc = False):
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

    def addFleetAdjacencies(self, nodes, coast):
        for i in nodes:
            self.addFleetAdjacency(i, coast == "nc", coast == "sc", coast == "ec", coast == "wc")

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
            case _:
                return False

    def orderLegal(self, order: Order):
        match order.ordering_unit.unit:
            case units.Army():
                return self.orderLegalArmy(order)
            case units.Fleet():
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

    def getArmyRetreats(self):
        for i in self.getArmyAdjacencies():
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)
    
    def getFleetRetreats(self):
        nc, sc, ec, wc = self.unit_coast == 0, self.unit_coast == 1, self.unit_coast == 2, self.unit_coast == 3
        for i in self.getFleetAdjacencies(nc, sc, ec, wc):
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)

    def dislodgeUnit(self):
        match self.unit:
            case units.Army():
                self.getArmyAdjacencies()
            case units.Fleet():
                self.getFleetAdjacencies()
        return super().dislodgeUnit()
