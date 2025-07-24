from orders import Order, Move, Hold, Support, Convoy, Disband, DisbandRetreat
import units

class Node:
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        self.name = name.lower()
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
        self.board = None
        self.convoy_check = False
        self.sim_check = False

    def getAllConvoys(self, actual, alllist, unitslist, queue, visited):
        if actual in visited:
            return alllist, unitslist, queue, visited
        visited.append(actual)

        aux1, aux2 = [], []
        for i in actual.getFleetAdjacencies():
            if type(i) == SeaTile:
                if i.unit is not None:
                    queue.append(i)
            elif type(i) == CoastTile or type(i) == MultipleCoastTile:
                alllist.append(i) 
                if i.unit is not None and type(i.unit) == units.Army:
                    unitslist.append(i)
        
        return alllist, unitslist, queue, visited

    def getAllLegalMoves(self):
        orders = [("h", self.name)]
        match self.unit:
            case units.Army():
                adj = self.getArmyAdjacencies()
                for i in adj:
                    orders.append(("m", self.name, i.name))
                    if i.unit is not None:
                        orders.append(("sh", self.name, i.name))
                
                for i in adj:
                    for j in i.getUniqueAdjacencies():
                        if j.unit is not None:
                            if j == self:
                                continue
                            if i in j.getCurrentAdjcencies():
                                orders.append(("sa", self.name, j.name, i.name))

                alllist = []
                queue = [self]
                visited = []
                
                while len(queue) > 0:
                    actual = queue.pop(0)
                    alllist, _, queue, visited = self.getAllConvoys(actual, alllist, [], queue, visited)

                for i in alllist:
                    if i == self:
                        continue
                    if i not in adj:
                        orders.append(("m", self.name, i.name))

            case units.Fleet():
                adj = self.getFleetAdjacencies()
                for i in adj:
                    orders.append(("m", self.name, i.name))
                    if i.unit is not None:
                        orders.append(("sh", self.name, i.name))

                for i in adj:
                    for j in i.getUniqueAdjacencies():
                        if j == self:
                            continue
                        if j.unit is not None:
                            orders.append(("sa", self.name, j.name, i.name))

                if type(self) == SeaTile:
                    alllist = []
                    unitslist = []
                    queue = [self]
                    visited = []
                    
                    while len(queue) > 0:
                        actual = queue.pop(0)
                        alllist, unitslist, queue, visited = self.getAllConvoys(actual, alllist, unitslist, queue, visited)

                    for i in unitslist:
                        for j in alllist:
                            if i == j:
                                continue
                            orders.append(("c", self.name, i.name, j.name))
            case _:
                pass
        
        return orders

    def getUniqueAdjacencies(self):
        a_adj = self.getArmyAdjacencies()
        f_adj = self.getFleetAdjacencies()
        adj = a_adj
        for i in f_adj:
            if i not in adj:
                adj.append(i)
        return adj

    def getCurrentAdjcencies(self):
        match self.unit:
            case units.Army():
                return self.getArmyAdjacencies()
            case units.Fleet():
                return self.getFleetAdjacencies()
            case _:
                return []

    def enemyUnitClose(self):
        if self.unit is None:
            return False
        adj = self.getUniqueAdjacencies()
        for i in adj:
            if i.unit is not None and i.unit.owner != self.unit.owner:
                return True
        return False

    def getFleetAdjacencies(self):
        pass

    def getArmyAdjacencies(self):
        pass

    def buildUnit(self, unit, coast=-1):
        match unit:
            case "a":
                u = units.Army(self, self.cored_by)
            case "f":
                u = units.Fleet(self, self.cored_by, coast)
        self.addUnit(u)

    def addUnit(self, unit):
        self.unit = unit
        self.holding_strength = 1

    def getValidRetreats(self):
        adj = []
        match self.dislodged_unit:
            case units.Army():
                adj = self.getArmyAdjacencies()
            case units.Fleet():
                adj = self.getFleetAdjacencies()
            case _:
                pass
        for i in adj:
            if i.militarized:
                continue
            if i.unit is not None:
                continue
            self.valid_retreats.append(i)

    def dislodgeUnit(self):
        # print("Dislodging...")
        self.dislodged_unit = self.getUnit()
        self.removeUnit()
        self.board.dislodged_units.append(self)

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
        # Add tapped if dislodged anyway
        if type(self.unit.order) == Support:
            for i in self.recieving_move_orders:
                if i.ordering_unit.orderLegal(i):
                    if type(self.unit.order.support_order) == Hold:
                        return True
                    if type(self.unit.order.support_order) == Move and i.ordering_unit != self.unit.order.support_order.destination:
                        return True
        return False
    
    def getUnit(self):
        return self.unit

    def moveUnit(self):
        # print("Preparing unit...", self.getUnit())
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
        self.convoy_check = False

    def resetRetreats(self):
        if self.dislodged_unit is not None:
            o = DisbandRetreat(self)
            o.executeOrder()
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
        print(f"Moving Unit - {str(self.moving_unit)}")
        print("<"*10)
        print()
        return ""


class InlandTile(Node):
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        self.army_adjacencies = []
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)

    def getUniqueAdjacencies(self):
        return self.getArmyAdjacencies()

    def getFleetAdjacencies(self):
        return []

    def getArmyAdjacencies(self):
        return self.army_adjacencies

    def addArmyAdjacency(self, node):
        self.army_adjacencies.append(node)
    
    def addArmyAdjacencies(self, nodes):
        for i in nodes:
            self.addArmyAdjacency(i)

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
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        self.fleet_adjacencies = []
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)

    def getUniqueAdjacencies(self):
        return self.getFleetAdjacencies()

    def getArmyAdjacencies(self):
        return []

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
                return False # No need to implement
            case _:
                # print("Not an order ._.")
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
    def __init__(self):
        self.fleet_adjacencies = []


class CoastTile(Node):
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by):
        self.army_adjacencies = []
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
                if order.destination in self.getArmyAdjacencies() or order.convoyed:
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
    def __init__(self, name, alias, node_placement, core, cored_by, owned_by, nc = False, sc = False, ec = False, wc = False):
        self.army_adjacencies = []
        self.coasts = [None, None, None, None]
        self.unit_coast = -1 # [nc, sc, ec, wc]
        super().__init__(name, alias, node_placement, core, cored_by, owned_by)
        if nc:
            self.coasts[0] = Coast()
        if sc:
            self.coasts[1] = Coast()
        if ec:
            self.coasts[2] = Coast()
        if wc:
            self.coasts[3] = Coast()

    def buildUnit(self, unit, coast=-1):
        match unit:
            case "a":
                u = units.Army(self, self.cored_by)
            case "f":
                u = units.Fleet(self, self.cored_by, coast)
        self.addUnit(u)

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

    def getFleetAdjacencies(self):
        nc, sc, ec, wc = self.unit_coast == 0, self.unit_coast == 1, self.unit_coast == 2, self.unit_coast == 3
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

    def getFleetAdjacenciesbyCoast(self, nc=False, sc=False, ec=False, wc=False):
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
                if order.destination in self.getArmyAdjacencies() or order.convoyed:
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
    
    def addUnit(self, unit, coast= -1):
        if self.unit is not None:
            self.dislodgeUnit()
        self.unit = unit
        self.holding_strength = 1
        self.unit_coast = coast
    
    def __str__(self):
        print(">"*10)
        print("NAME -", self.name)
        for j in self.alias:
            print(j, end=", ")
        print("-"*10)
        print(f"Sc - {self.core}")
        print(f"Owned by - {str(self.owned_by)}")
        print(f"Cored by - {str(self.cored_by)}")
        print(f"Unit - {str(self.unit)}", str(self.unit_coast))
        print(f"Dislodged Unit - {str(self.dislodged_unit)}")
        print(f"Moving Unit - {str(self.moving_unit)}")
        print("<"*10)
        print()
        return ""
