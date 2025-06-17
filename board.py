from orders import Order, Move, Hold, Support, Convoy, Retreat, Build, Disband, DisbandRetreat
from graph import Node, InlandTile, SeaTile, CoastTile, MultipleCoastTile
from units import Unit, Army, Fleet
from country import Country
from pyvis.network import Network
import colorsys

class Board:
    def __init__(self, nodes, countries, phase="spring", year=1901):
        self.node_id = {}
        self.country_id = {}
        self.nodes = nodes
        self.countries = countries
        for idx, i in enumerate(nodes):
            i.board = self
            self.node_id[i.name] = idx
        for idx, i in enumerate(countries):
            self.country_id[i.name] = idx
        self.move_orders = []
        self.other_orders = []
        self.successful_moves = []
        self.dislodged_units = []
        self.year = year
        try: 
            self.phase = phase.lower() # Spring / spring_retreats / Fall / fall_retreats / Winter
            assert(self.phase.lower() in ["spring", "spring_retreats", "fall", "fall_retreats", "winter"])
        except:
            self.phase = "spring"
            print("Error: Unknown phase, defaulted to Spring Moves\n<> Valid options:", ["spring", "spring_retreats", "fall", "fall_retreats", "winter"], "<>")

    def importBoardState(self, file):
        with open(file, 'r') as file:
            phase, units, provinces = file.read().split("---")

            # PHASE
            self.phase = phase.split(", ")[0].lower()
            self.year = int(phase.split(", ")[1][:-1]) # removing \n

            # UNITS
            for i in units.split("\n")[1:][:-1]:
                unit = i.split(", ")
                coast = None
                if len(unit) == 3:
                    c = unit[0]
                    t = unit[1]
                    p = self.getNode(unit[2])
                else:
                    c = unit[0]
                    t = unit[1]
                    p = self.getNode(unit[2])
                    coast = unit[3]
                
                count = self.getCountry(c)
                match t:
                    case "A":
                        Army(p, count)
                    case "F":
                        if coast is None:
                            Fleet(p, count)
                        else:
                            coasts = {"nc": 0, "sc": 1, "ec": 2, "wc": 3}
                            Fleet(p, count, coasts[coast])

            # OWNED PROVINCES 
            for i in provinces.split("\n")[1:]:
                p = i.split(", ")
                province = self.getNode(p[0])
                country = self.getCountry(p[1])
                country.addProvince(province)

    def createBoardFromFile(file):
        with open(file, 'r') as file:
            provinces, armyadj, fleetadj, countries = file.read().split("---")

            # PROVINCES
            allprovinces = {}
            for i in provinces.split("\n")[:-1]:
                split = i.split(", ")
                if len(split) == 3:
                    name, t, core, x, y = split
                else:
                    name = split[0]
                    t = split[1]
                    core = split[2]
                    x = split[3]
                    y = split[4]
                    coasts = split[5:]

                province = None

                core = core == "y"
                match t:
                    case "i":
                        province = InlandTile(name, [], (int(x), int(y)), core, None, None)
                    case "s":
                        province = SeaTile(name, [], (int(x), int(y)), core, None, None)
                    case "c":
                        province = CoastTile(name, [], (int(x), int(y)), core, None, None)
                    case "mc":
                        province = MultipleCoastTile(name, [], (int(x), int(y)), core, None, None, "nc" in coasts, "sc" in coasts, "ec" in coasts, "wc" in coasts)
                    case _:
                        pass

                allprovinces[name] = province

            # ARMY ADJACENCIES
            for i in armyadj.split("\n")[1:-1]:
                a, b = i.split(" - ")
                allprovinces[a].addArmyAdjacency(allprovinces[b])
                allprovinces[b].addArmyAdjacency(allprovinces[a])

            # FLEET ADJACENCIES
            for i in fleetadj.split("\n")[1:-1]:
                a, b = i.split(" - ")
                coasta = None
                coastb = None
                if len(a.split(", ")) == 2:
                    coasta = a.split(", ")[1]
                    a = a.split(", ")[0]
                if len(b.split(", ")) == 2:
                    coastb = b.split(", ")[1]
                    b = b.split(", ")[0]

                if coasta is None:
                    allprovinces[a].addFleetAdjacency(allprovinces[b])
                else: 
                    aux = a.split(", ")
                    allprovinces[aux[0]].addFleetAdjacency(allprovinces[b], 'nc' == coasta, 'sc' == coasta, 'ec' == coasta, 'wc' == coasta)

                if coastb is None:
                    allprovinces[b].addFleetAdjacency(allprovinces[a])
                else: 
                    aux = b.split(", ")
                    allprovinces[aux[0]].addFleetAdjacency(allprovinces[a], 'nc' == coastb, 'sc' == coastb, 'ec' == coastb, 'wc' == coastb)

            # COUNTRIES
            count = []
            for i in countries.split("\n")[1:]:
                country = i.split(", ")
                c = Country(country[0], [], [], [])
                for j in country[1:]:
                    province = allprovinces[j]
                    c.addCore(province)
                count.append(c)

            b = Board(list(allprovinces.values()), count)

            return b

    def getNode(self, str) -> Node:
        return self.nodes[self.node_id[str.lower()]]

    def getCountry(self, str) -> Country:
        return self.countries[self.country_id[str.lower()]]

    def printOrders(self):
        for i in self.move_orders:
            print(i)
        for i in self.other_orders:
            print(i)

    def parseOrder(self, str) -> Order:
        str = str.split(" ")
        match str[1].lower():
            case "":
                return
            case "m" | "-" | "r":
                print(self.phase)
                if self.phase in ["spring", "fall"]:
                    print("Move!")
                    ordering_unit = self.getNode(str[0])
                    destination = self.getNode(str[2])
                    order = Move(ordering_unit, destination)
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
                return order
            case "s" | "support" | "supports":
                print("Support!")
                if self.phase in ["spring_retreats", "fall_retreats", "winter"]:
                    print("Invalid order in this phase")
                    return
                if str[3].lower() in ["h", "hold", "holds"]:
                    ordering_unit = self.getNode(str[0])
                    destination = self.getNode(str[2])
                    order = Support(ordering_unit, Hold(destination))
                    return order
                elif str[3].lower() in ["m", "-"]:
                    ordering_unit = self.getNode(str[0])
                    moving_unit = self.getNode(str[2])
                    destination = self.getNode(str[4])
                    order = Support(ordering_unit, Move(moving_unit, destination, add_order=False))
                    return order
                else:
                    print("Parsing Error")
            case "c" | "convoy" | "convoys":
                print("Convoy!")
                if self.phase in ["spring_retreats", "fall_retreats", "winter"]:
                    print("Invalid order in this phase")
                    return
                ordering_unit = self.getNode(str[0])
                if type(ordering_unit.unit) == Fleet:
                    order = Convoy(ordering_unit, Move(self.getNode(str[2]), self.getNode(str[4]), add_order=False))
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
                        if core.owned_by != core.cored_by:
                            print("Can't build here")
                            return
                        if len(str) == 3:
                            str.append(-1)
                        else:
                            coasts = {'nc': 0, 'sc': 1, 'ec': 2, 'wc': 3}
                            str[3] = coasts[str[3]]
                        order = Build(core, str[1], str[3])
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

    def checkMovesAgain(self, order: Move):
        if order.checked:
            order.checked = False
            res = self.checkMoves(order)
            try: 
                if not res:
                    self.successful_moves.remove(order)
            except:
                pass
            for o in order.ordering_unit.recieving_move_orders:
                self.checkMovesAgain(o)

    def getConvoyPath(self, actual, nodes, end, path = []):
        actual.convoy_check = True
        path.append(actual)
        if actual == end:
            return path
        for i in actual.getFleetAdjacencies():
            if i in nodes and not i.convoy_check:
                aux = self.getConvoyPath(i, nodes, end, path)
                if len(aux) != 0:
                    return aux
        return []

    def checkMoves(self, order):
        print(order)
        if order.checked:
            print("Already checked")
            return order.success
        order.checked = True

        # Check if legal
        order.legal = order.ordering_unit.orderLegal(order)
        if not order.legal:
            print(order, order.convoyed)
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
                if order.destination.unit.order.success or order.destination.unit.order.witing_on_result:
                    return True
            else: 
                order.witing_on_result = True
                order.destination.unit.order.success = self.checkMoves(order.destination.unit.order)
                order.witing_on_result = False
                if order.destination.unit.order.success:
                    print("Success!")
                    self.successful_moves.append(order.destination.unit.order)
                    return True

        # Same country
        if order.destination.unit is not None and order.ordering_unit.unit.owner == order.destination.unit.owner:
            print("Moving against a unit with the same country", order.ordering_unit.unit.owner.name, order.destination.unit.owner.name)
            return False
        
        # Remove supports into allied unit
        for o in order.supports:
            if order.destination.unit is not None and order.ordering_unit.unit is not None and o.ordering_unit.unit.owner == order.destination.unit.owner:
                print("Removing support into an allied unit", o.ordering_unit.unit.owner, order.destination.unit.owner)
                order.ordering_unit.unit.attacking_strength -= 1

        # Strength check
        if order.ordering_unit.unit.attacking_strength <= order.destination.holding_strength:
            print("Not enough strength", order.ordering_unit.unit.attacking_strength, order.destination.holding_strength)
            return False

        # Check if you're dislodging a support
        if order.destination.unit is not None:
            affected_order = order.destination.unit.order
            if type(affected_order) == Support and not affected_order.tapped and affected_order.legal:
                print("Dislodged support: ", affected_order.ordering_unit.name)
                affected_order.tapped = True
                match affected_order.support_order:
                    case Move():
                        affected_order.ordering_unit.unit.attacking_strength -= 1
                        if affected_order.checked:
                            affected_order.checked = False
                            res = self.checkMoves(affected_order)
                            try: 
                                if not res:
                                    self.successful_moves.remove(affected_order)
                            except:
                                pass
                            for o in affected_order.ordering_unit.recieving_move_orders:
                                self.checkMovesAgain(o)
                    case Hold():
                        affected_order.support_order.ordering_unit.holding_strength -= 1
                        for o in affected_order.support_order.ordering_unit.recieving_move_orders:
                            self.checkMovesAgain(o)
        
        # # TODO change Check if you're dislodging a convoy
        # if order.destination.unit is not None:
        #     affected_order = order.destination.unit.order
        #     if type(affected_order) == Convoy and affected_order.valid:
        #         print("Convoy support: ", affected_order.ordering_unit.name)
        #         affected_order.ordering_unit.unit.attacking_strength -= 1
        #         if affected_order.checked:
        #             affected_order.checked = False
        #             res = self.checkMoves(affected_order)
        #             try: 
        #                 if not res:
        #                     self.successful_moves.remove(affected_order)
        #             except:
        #                 pass
        #             for o in affected_order.ordering_unit.recieving_move_orders:
        #                 self.checkMovesAgain(o)
        return True

    def adjudicateMoves(self):
        self.convoys = []
        self.successful_moves = []
        print("Adju!")
        for order in self.other_orders:
            order.ordering_unit.hold = True

        # Adjudicate supports
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
                                    print("Support", order)
                                    # Check if the unit is doing the same move as the support
                                    if type(order.support_order.ordering_unit.unit.order) == Move:
                                        if order.support_order == order.support_order.ordering_unit.unit.order:
                                            order.support_order.ordering_unit.unit.order.supports.append(order)
                                            order.support_order.ordering_unit.unit.attacking_strength += 1
                            case Hold():
                                if order.legal and order.support_order.ordering_unit.hold:
                                    order.support_order.ordering_unit.holding_strength += 1
                    else:
                        order.fail = True
                case Convoy():
                    if type(order.ordering_unit) == SeaTile:
                        self.convoys.append(order)
                case _:
                    pass

        for order in self.convoys:
            if not order.checked:
                order.checked = True
                if order.move.ordering_unit.unit.order == order.move:
                    convoyed_unit = order.move.ordering_unit.unit
                    print(order.move.ordering_unit, convoyed_unit.order)
                    fleetadj = order.ordering_unit.getFleetAdjacencies()

                    if order.move.ordering_unit in fleetadj and order.move.destination in fleetadj:
                        convoyed_unit.order.convoy_start = order.ordering_unit
                        convoyed_unit.order.convoy_end = order.ordering_unit
                        convoyed_unit.order.convoyed = True
                        print("Convoy:", order, convoyed_unit.order.convoyed)

                    elif order.move.ordering_unit in fleetadj:
                        convoyed_unit.order.convoy_start = order.ordering_unit
                        convoyed_unit.order.convoy_path.append(order.ordering_unit)

                    elif order.move.destination in fleetadj:
                        convoyed_unit.order.convoy_end = order.ordering_unit
                        convoyed_unit.order.convoy_path.append(order.ordering_unit)
                    
                    else:
                        for i in order.ordering_unit.getFleetAdjacencies():
                            if type(i.unit.order) == Convoy and i.unit.order.move == order.move:
                                convoyed_unit.order.convoy_path.append(order.ordering_unit)
                    
                    if convoyed_unit.order.convoy_start is not None and convoyed_unit.order.convoy_end is not None and not convoyed_unit.order.convoyed:
                        convoy = self.getConvoyPath(convoyed_unit.order.convoy_start, convoyed_unit.order.convoy_path, convoyed_unit.order.convoy_end)
                        if len(convoy) != 0:
                            convoyed_unit.order.convoyed = True


        for order in self.move_orders:
            order.ordering_unit.hold = False
            order.success = self.checkMoves(order)
            if order.success:
                print("Success!")
                self.successful_moves.append(order)

        for i in self.successful_moves:
            print(i)
            i.ordering_unit.moveUnit()

        for i in self.successful_moves:
            i.executeOrder()

        for i in self.dislodged_units:
            print(i)
            i.getValidRetreats()

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

    def claimFall(self):
        for c in self.countries:
            for u in c.units:
                print(u, u.node.name)
                p = u.node
                if not p.core:
                    continue
                if self.getNode('den') == p:
                    print('DEN!!!')
                    for i in c.provinces:
                        print(i)
                if p not in c.provinces:
                    print("owo")
                    c.addProvince(p)

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
                self.claimFall()
                return

            case "fall_retreats":
                self.adjudicateRetreats()
                self.phase = "winter"
                for i in self.nodes:
                    i.resetRetreats()
                self.claimFall()
                return

            case "winter":
                self.adjudicateWinter()
                self.phase = "spring"
                self.year += 1
                return

    def printGraph(self):
        net = Network(width=2000, height=2000)
        n = len(self.countries)
        HSV_tuples = [(x*1.0/n, 0.5, 0.5) for x in range(n)]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))
        names = [i.name for i in self.nodes]
        color = [RGB_tuples[self.country_id[i.owned_by.name]] if i.owned_by is not None
                 else (0.5, 0.5, 0.5) if type(i) != SeaTile
                 else (0.1, 0.1, 0.3)
                 for i in self.nodes]
        color = ['#{:02x}{:02x}{:02x}'.format(int(i[0]*255), int(i[1]*255), int(i[2]*255)) for i in color]
        shape = ['dot' if i.unit is None
                 else 'triangle' if type(i.unit) == Fleet
                 else 'square' if type(i.unit) == Army
                 else 'star'
                 for i in self.nodes]
        x = [i.node_placement[0]*50 for i in self.nodes]
        y = [abs(i.node_placement[1]-25)*50 for i in self.nodes]
        size = [10 for i in self.nodes]
        pos = [str(i.node_placement) for i in self.nodes]
        net.add_nodes(names, title=pos, color=color, shape=shape, x=x, y=y, size=size, label=names)
        for i in self.nodes:
            for j in i.getArmyAdjacencies():
                net.add_edge(i.name, j.name)
            for j in i.getFleetAdjacencies():
                net.add_edge(i.name, j.name, color="#7f7f7f")
        net.toggle_physics(False)
        net.show("board.html", notebook=False)

    def __str__(self):
        print(f"YEAR {self.year}, PHASE: {self.phase}")
        print("SCOREBOARD")
        for i in self.countries:
            print("{:9s} {:3d}\t{:+}".format(i.name, i.getScore(), i.getAdjustments()))
        return ""

