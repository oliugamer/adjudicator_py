from orders import Order, Move, Hold, Support, Convoy, Retreat, Build, Disband, DisbandRetreat
from graph import Node
from units import Unit, Army, Fleet

class Board:
    def __init__(self, nodes, countries, phase="spring", year=1901):
        self.node_id = {}
        self.nodes = nodes
        self.countries = countries
        for idx, i in enumerate(nodes):
            self.node_id[i.name] = idx
        self.move_orders = []
        self.other_orders = []
        self.successful_moves = []
        self.year = year
        try: 
            self.phase = phase.lower() # Spring / spring_retreats / Fall / fall_retreats / Winter
            assert(self.phase.lower() in ["spring", "spring_retreats", "fall", "fall_retreats", "winter"])
        except:
            self.phase = "spring"
            print("Error: Unknown phase, defaulted to Spring Moves\n<> Valid options:", ["spring", "spring_retreats", "fall", "fall_retreats", "winter"], "<>")

    def getNode(self, str) -> Node:
        return self.nodes[self.node_id[str]]

    def printOrders(self):
        for i in self.move_orders:
            print(i)
        for i in self.other_orders:
            print(i)

    def parseOrder(self, str, country=None) -> Order:
        # TODO actually implement countries
        str = str.split(" ")
        match str[1].lower():
            case "":
                return
            case "m" | "-" | "r":
                if self.phase in ["spring", "fall"]:
                    print("Move!")
                    ordering_unit = self.getNode(str[0])
                    destination = self.getNode(str[2])
                    order = Move(ordering_unit, destination)
                    destination.recieving_move_orders.append(order)
                    order.ordering_unit.unit.attacking_strength = 1
                    return order
                if self.phase in ["spring_retreats", "fall_retreats"]:
                    ordering_unit = self.getNode(str[0])
                    destination = self.getNode(str[2])
                    order = Retreat(ordering_unit, destination)
                    return order
                print("Invalid order in this phase")
                return
            case "h" | "hold" | "holds":
                print("Hold!")
                if self.phase in ["spring_retreats", "fall_retreats", "winter"]:
                    print("Invalid order in this phase")
                    return
                ordering_unit = self.getNode(str[0])
                order = Hold(ordering_unit)
                order.ordering_unit.unit.attacking_strength = 0
                return order
            case "s" | "support" | "supports":
                print("Support!")
                if self.phase in ["spring_retreats", "fall_retreats", "winter"]:
                    print("Invalid order in this phase")
                    return
                if str[3].lower() in ["h", "hold", "holds"]:
                    ordering_unit = self.getNode(str[0])
                    destination = self.getNode(str[2])
                    order = Support(ordering_unit, destination)
                    order.ordering_unit.unit.attacking_strength = 0
                    # self.getNode(str[2]).recieving_orders.append(order)
                    return order
                elif str[3].lower() in ["m", "-"]:
                    ordering_unit = self.getNode(str[0])
                    moving_unit = self.getNode(str[2])
                    destination = self.getNode(str[4])
                    order = Support(ordering_unit, Move(moving_unit, destination))
                    order.ordering_unit.unit.attacking_strength = 0
                    # self.getNode(str[2]).recieving_orders.append(order)
                    return order
                else:
                    print("Parsing Error")
            case "c" | "convoy" | "convoys":
                print("Convoy!")
                if self.phase in ["spring_retreats", "fall_retreats", "winter"]:
                    print("Invalid order in this phase")
                    return
                ordering_unit = self.getNode(str[0])
                if type(ordering_unit.unit) == Fleet():
                    order = Convoy(ordering_unit, Move(self.getNode(str[2]), self.getNode(str[4])))
                    return order
                print("Error: An army can't order a convoy")
            
            case "d" | "disband":
                print("Disband!")
                if self.phase in ["spring", "fall"]:
                    print("Invalid order in this phase")
                    return
                if self.getNode(str[0]).unit is None:
                    print("No unit to disband :P")
                    return
                if self.phase in ["spring_retreats", "fall_retreats"]:
                    order = DisbandRetreat(self.getNode(str[0]))
                else:
                    order = Disband(self.getNode(str[0]))
                return order

            case _:
                match str[0].lower():
                    case "b" | "build":
                        print("Build!")
                        if self.phase in ["spring_retreats", "fall_retreats", "spring", "fall"]:
                            print("Invalid order in this phase")
                            return
                        core = self.getNode(str[1])
                        if not core.core:
                            print("Not a core")
                            return
                        units = {"a": Army(), "f": Fleet()}
                        order = Build(core, units[str[1]])
                        return order
                    case "d" | "disband":
                        print("Disband!")
                        if self.phase in ["spring", "fall"]:
                            print("Invalid order in this phase")
                            return
                        if self.getNode(str[1]).unit is None:
                            print("No unit to disband :P")
                            return
                        if self.phase in ["spring_retreats", "fall_retreats"]:
                            order = DisbandRetreat(self.getNode(str[1]))
                        else:
                            order = Disband(self.getNode(str[1]))
                        return order
                print("Parsing Error")
        
    def addOrder(self, str):
        order = self.parseOrder(str)
        order.ordering_unit.unit.order = order
        print(order)
        if order is None:
            return
        # TODO remove past order if updated
        if type(order) == Move:
            self.move_orders.append(order)
        else: 
            self.other_orders.append(order)

    def addRawOrder(self, order):
        if type(order) == Move:
            self.move_orders.append(order)
        else: 
            self.other_orders.append(order)

    def resetOrders(self):
        self.move_orders = []
        self.other_orders = []

    def checkMoves(self, order):
        print(order)
        if order.checked:
            print("Already checked")
            return False
        order.checked = True

        # Check if legal
        order.legal = order.ordering_unit.orderLegal(order)
        if not order.legal:
            print("Not legal")
            return False

        order.destination.militarized = True

        # Bounce
        print("Recieving move orders", order.destination.name, order.destination.recieving_move_orders)
        for i in order.destination.recieving_move_orders:
            if i == order:
                continue
            print("Check bounce with", i)
            if order.ordering_unit.unit.attacking_strength <= i.ordering_unit.unit.attacking_strength:
                print("Bounced", order.ordering_unit.unit.attacking_strength, i.ordering_unit.unit.attacking_strength)
                return False

        # Check if the unit in the province ahead is moving out
        if order.destination.unit is not None and type(order.destination.unit.order) == Move:
            print("Checking other moves...")
            if order.destination.unit.order.checked:
                if order.destination.unit.order.success:
                    return True
            else: 
                order.destination.unit.order.success = self.checkMoves(order.destination.unit.order)
                if order.destination.unit.order.success:
                    print("Success!")
                    self.successful_moves.append(order.destination.unit.order)
                    return True
        
        # Strength Check
        if order.ordering_unit.unit.attacking_strength <= order.destination.holding_strength and order.destination.hold:
            print("Not enough strength", order.ordering_unit.unit.attacking_strength, order.destination.holding_strength)
            return False

        # Same country
        if order.destination.unit is not None and order.ordering_unit.unit.owner == order.destination.unit.owner:
            print("Moving against a unit with the same country", order.ordering_unit.unit.owner.name, order.destination.unit.owner.name)
            return False

        return True

    def adjudicateMoves(self):
        print("Adju!")
        for order in self.other_orders:
            order.support_order.ordering_unit.hold = True

        for order in self.other_orders:
            order.legal = order.ordering_unit.orderLegal(order)
            match order:
                case Hold():
                    pass
                case Support():
                    print("Tapped support:", order.ordering_unit.isTapped())
                    if not order.ordering_unit.isTapped():
                        match order.support_order:
                            case Move():
                                if order.support_order.ordering_unit.unit is not None and order.legal:
                                    print("Support", order, order.ordering_unit.unit.owner, order.support_order.destination.unit.owner)
                                    # Check if the unit is doing the same move as the support
                                    if order.support_order == order.support_order.ordering_unit.unit.order:
                                        # Check that the unit is not from the same country
                                        # TODO remove check if the unit is leaving
                                        if order.support_order.destination.unit.owner is not None and order.ordering_unit.unit.owner != order.support_order.destination.unit.owner:
                                            order.support_order.ordering_unit.unit.attacking_strength += 1
                            case Hold():
                                if order.legal and order.support_order.ordering_unit.hold:
                                    order.support_order.ordering_unit.holding_strength += 1
                    else:
                        order.fail = True
                case Convoy():
                    # TODO
                    pass
                case _:
                    pass

        for order in self.move_orders:
            order.success = self.checkMoves(order)
            if order.success:
                print("Success!")
                self.successful_moves.append(order)

        for i in self.successful_moves:
            i.ordering_unit.moveUnit()

        for i in self.successful_moves:
            i.executeOrder()

        self.resetOrders()

    def adjudicateRetreats(self):
        for order in self.other_orders:
            match order:
                case Retreat():
                    if order.destination in order.ordering_unit.valid_retreats:
                        order.executeOrder()
                case Disband():
                    order.executeOrder()
        
        self.resetOrders()

    def adjudicateWinter(self):
        for order in self.other_orders:
            order.executeOrder()

    def adjudicate(self):
        match self.phase:
            case "spring":
                self.adjudicateMoves()
                self.phase = "spring_retreats"
                for i in self.nodes:
                    i.resetAfterAdju()
                return

            case "spring_retreats":
                self.adjudicateRetreats()
                self.phase = "fall"
                for i in self.nodes:
                    i.resetRetreats()
                return

            case "fall":
                self.adjudicateMoves()
                self.phase = "fall_retreats"
                for i in self.nodes:
                    i.resetAfterAdju()
                # TODO claim all provinces and update score
                return

            case "fall_retreats":
                self.adjudicateRetreats()
                self.phase = "winter"
                for i in self.nodes:
                    i.resetRetreats()
                return

            case "winter":
                self.adjudicateWinter()
                self.phase = "spring"
                self.year += 1
                return

    def __str__(self):
        print(f"YEAR {self.year}, PHASE: {self.phase}")
        for i in self.nodes:
            str(i)
        return ""

