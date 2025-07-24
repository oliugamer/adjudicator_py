from metrics import Metrics
from board import Board
from orders import Move, Hold, Support, Convoy, Retreat, Disband, DisbandRetreat, Build
from units import Army, Fleet
from graph import InlandTile, MultipleCoastTile
from heuristics import SimHeuristic
import random
import time
from joblib import Parallel, delayed
import csv
import os

class Simulation:
    def __init__(self, board):
        self.currentboard = board.copy()
        self.newboard = None
        self.simval = 5

    def checkMoves(self, moving_unit, destination):
        value = 0.1
        if moving_unit.core and moving_unit.owned_by != moving_unit.unit.owner:
            value -= 0.5
        elif moving_unit.core and moving_unit.enemyUnitClose():
            value -= 0.25

        if destination.core and destination.owned_by != moving_unit.unit.owner:
            if destination.unit is None:
                value += 1
            else:
                value += 0.2

        aux = 0
        adj = destination.getUniqueAdjacencies()
        for i in adj:
            if i.core and i.owned_by != moving_unit.owned_by:
                aux += 1
        value += min(aux/len(adj), 0.4)

        return min(1, max(0.1, value))

    def checkorder(self, o):
        value = 0
        match o[0]:
            case "m":
                ordering_unit = self.currentboard.getNode(o[1])
                destination = self.currentboard.getNode(o[2])
                value = self.checkMoves(ordering_unit, destination)
            case "h":
                ordering_unit = self.currentboard.getNode(o[1])
                if ordering_unit.core and ordering_unit.enemyUnitClose():
                    value = 0.3
                else:
                    value = 0.1
            case "sh":
                ordering_unit = self.currentboard.getNode(o[1])
                destination = self.currentboard.getNode(o[2])
                if destination.core and destination.enemyUnitClose():
                    value = 0.5
                else:
                    value = 0.1
            case "sa":
                ordering_unit = self.currentboard.getNode(o[1])
                moving_unit = self.currentboard.getNode(o[2])
                destination = self.currentboard.getNode(o[3])
                if ordering_unit.owned_by == moving_unit.owned_by:
                    value = self.checkMoves(moving_unit, destination)
                else:
                    value = 0.1
            case "c":
                ordering_unit = self.currentboard.getNode(o[1])
                moving_unit = self.currentboard.getNode(o[2])
                destination = self.currentboard.getNode(o[3])
                value = max(self.checkMoves(moving_unit, destination) - 0.1, 0.1)
        return value

    def getCountryOrders(self, country):
        orders = []
        for i in country.units:
            orders.append(i.node.getAllLegalMoves())
        return orders

    def getAllOrders(self, units):
        orders = []
        for i in units:
            orders.append(i.getAllLegalMoves())
        return orders

    def getAllUnits(self):
        units = []
        for i in self.currentboard.nodes:
            if i.unit is not None:
                units.append(i)
        return units

    def generateRandomMoveSet(self, probs):
        countmoves = []
        for idx, i in enumerate(probs[0]):
            aux = random.random()
            for j in range(len(i)):
                aux -= probs[2][idx][j]
                if aux < 0:
                    countmoves.append(i[j])
                    break
        # print(countmoves)
        return countmoves

    def simulateRetreats(self, board):
        for i in board.dislodged_units:
            aux = random.choice(i.valid_retreats + [None])
            if aux is None:
                DisbandRetreat(i)
            else:
                Retreat(i, aux)
        board.adjudicate()

    def parseMoveOrders(self, board, o):
        match o[0]:
            case "m":
                ordering_unit = board.getNode(o[1])
                destination = board.getNode(o[2])
                order = Move(ordering_unit, destination)
            case "h":
                ordering_unit = board.getNode(o[1])
                order = Hold(ordering_unit)
            case "sh":
                ordering_unit = board.getNode(o[1])
                destination = board.getNode(o[2])
                order = Support(ordering_unit, Hold(destination, add_order=False))
            case "sa":
                ordering_unit = board.getNode(o[1])
                moving_unit = board.getNode(o[2])
                destination = board.getNode(o[3])
                order = Support(ordering_unit, Move(moving_unit, destination, add_order=False))
            case "c":
                ordering_unit = board.getNode(o[1])
                moving_unit = board.getNode(o[2])
                destination = board.getNode(o[3])
                order = Convoy(ordering_unit, Move(moving_unit, destination, add_order=False))
            case _:
                pass
        return order

    def simOtherMoves(self, count, orders, cmoves):
        othermoves = []

        for c2 in self.currentboard.countries:
            if c2 == count:
                continue
            othermoves += self.generateRandomMoveSet(orders[c2.name])

        self.newboard = self.currentboard.copy()
        
        othermoves += cmoves
        for i in othermoves:
            order = self.parseMoveOrders(self.newboard, i)
            self.newboard.addRawOrder(order)

        self.newboard.adjudicate()

        self.simulateRetreats(self.newboard)

        h = SimHeuristic(self.newboard)
        return h.evaluatePosition(self.newboard.getCountry(count.name))

    def simulateOneMovePhase(self, iterc1=10, iterc2=10):
        # units = self.getAllUnits()
        orders = {}

        for i in self.currentboard.countries:
            aux = self.getCountryOrders(i)
            orders[i.name] = (aux, [], [])
            for unit in aux:
                maxval = 0
                val = []
                for j in unit:
                    val.append(self.checkorder(j))
                    maxval += val[-1]
                orders[i.name][1].append(val)

                val2 = []
                for j in range(len(unit)):
                    val2.append(val[j]/maxval)
                orders[i.name][2].append(val2)

        vals = {}
        moveset = {}
        for count in self.currentboard.countries:
            vals[count.name] = float('-inf')
            for _ in range(iterc1):
                cmoves = self.generateRandomMoveSet(orders[count.name])

                res = Parallel()(delayed(self.simOtherMoves)(count, orders, cmoves) for _ in range(iterc2))
                # res = []
                # for _ in range(iterc2):
                #     res.append(self.simOtherMoves(count, orders, cmoves))

                if vals[count.name] < sum(res)/iterc2:
                    vals[count.name] = sum(res)/iterc2
                    moveset[count.name] = cmoves

        # print(vals, moveset)
        return moveset

    def evaluateArmy(self, node):
        adj = node.getArmyAdjacencies()
        enemyu1 = 0
        enemyu2 = 0
        for i in adj:
            if i.unit is not None and i.unit.owner != node.cored_by:
                enemyu1 += 1
            for j in i.getArmyAdjacencies():
                if j.unit is not None and j.unit.owner != node.cored_by and j not in adj:
                    enemyu2 += 1

        return enemyu1*5 + enemyu2
    
    def evaluateFleet(self, node, coast=None):
        if coast is None:
            adj = node.getFleetAdjacencies()
        else:
            adj = coast.fleet_adjacencies
        enemyu1 = 0
        enemyu2 = 0
        for i in adj:
            if i.unit is not None and i.unit.owner != node.cored_by:
                enemyu1 += 1

            adj2 = i.getFleetAdjacencies()
            if len(i.getFleetAdjacencies()) == 0:
                for j in i.coasts:
                    if j is not None:
                        for k in j.fleet_adjacencies:
                            if k == i:
                                adj2 = j.fleet_adjacencies
            
            for j in adj2:
                if j.unit is not None and j.unit.owner != node.cored_by and j not in adj:
                    enemyu2 += 1

        return enemyu1*5 + enemyu2

    def eveluateBuild(self, node):
        if type(node) == InlandTile:
            val = self.evaluateArmy(node)
            return ("A", node.name, val)
        if type(node) == MultipleCoastTile:
            valA = self.evaluateArmy(node)
            valF = 0
            coasts = ["nc", "sc", "ec", "wc"]
            coast = None
            for idx, i in enumerate(node.coasts):
                if i is not None:
                    v = self.evaluateFleet(node, i)
                    if v > valF:
                        valF = v
                        coast = coasts[idx]
                    elif v == valF and coast is None:
                        valF = v
                        coast = coasts[idx]
                    elif v == valF:
                        valF, coast = random.choice([(valF, coast), (v, coasts[idx])])
            if valA > valF:
                return ("A", node.name, valA)
            elif valF > valA:
                return ("F,"+coast, node.name, valF)
            else:
                return random.choice([("A", node.name, valA), ("F,"+coast, node.name, valF)])
        else: 
            valA = self.evaluateArmy(node)
            valF = self.evaluateFleet(node)
            if valA > valF:
                return ("A", node.name, valA)
            elif valF > valA:
                return ("F", node.name, valF)
            else:
                return random.choice([("A", node.name, valA), ("F", node.name, valF)])

    def closerSC(self, current, value, type, country):
        if current.sim_check:
            return 
        
        if value > self.simval:
            return

        if current.owned_by == country and current.core:
            if value < self.simval:
                self.simval = value
                return 

        current.sim_check = True

        if type == "a":
            for i in current.getArmyAdjacencies():
                self.closerSC(i, value+1, type, country)
        elif type == "f":
            for i in current.getFleetAdjacencies():
                self.closerSC(i, value+1, type, country)

        current.sim_check = False
        return

    def eveluateDisband(self, unit):
        if unit.node.core:
            return -5
        ut = "a" if type(unit) == Army else "f"
        self.simval = 5
        self.closerSC(unit.node, 0, ut, unit.owner)
        return self.simval
        
    def simulateWinterMoves(self):
        moveset = {}
        for i in self.currentboard.countries:
            possible_orders = []
            adj = i.getAdjustments()
            if adj > 0: # Builds
                for core in i.cores:
                    if core.owned_by == i and core.unit is None:
                        possible_orders.append(self.eveluateBuild(core))

            elif adj < 0: # Disbands
                for unit in i.units:
                    possible_orders.append(("D", unit, self.eveluateDisband(unit)))

            moveset[i.name] = []

            aux = sorted(possible_orders, key=lambda order: order[2])
            for j in range(min(abs(adj), len(aux))):
                moveset[i.name].append(aux[-(j+1)][:-1])
        # print(moveset)
        return moveset

    def parseWinterOrders(self, board, o):
        match o[0]:
            case "A":
                order = Build(board.getNode(o[1]), "a")
            case "F":
                order = Build(board.getNode(o[1]), "f")
            case "D":
                order = Disband(o[1])
            case _:
                coast = o[0].split(",")[1]
                coasts = {"nc": 0, "sc": 1, "ec": 2, "wc": 3}
                order = Build(board.getNode(o[1]), "f", coasts[coast])
        return order

    def simulateYear(self, iter1=10, iter2=10):
        # Spring
        print("Spring")
        orders = self.simulateOneMovePhase(iter1, iter2)
        for i in orders.values():
            for j in i:
                order = self.parseMoveOrders(self.currentboard, j)
                self.currentboard.addRawOrder(order)
        self.currentboard.adjudicate()

        print("Retreats")
        # Retreats
        self.simulateRetreats(self.currentboard)

        print("Fall")
        # Fall
        orders = self.simulateOneMovePhase(iter1, iter2)
        for i in orders.values():
            for j in i:
                order = self.parseMoveOrders(self.currentboard, j)
                self.currentboard.addRawOrder(order)
        self.currentboard.adjudicate()

        print("Retreats")
        # Retreats
        self.simulateRetreats(self.currentboard)

        print("Winter")
        # Winter
        print(self.currentboard)
        orders = self.simulateWinterMoves()
        for i in orders.values():
            for j in i:
                order = self.parseWinterOrders(self.currentboard, j)
                self.currentboard.addRawOrder(order)
        self.currentboard.adjudicate()

    def simulateGame(self, maxyear=10, iter1=10, iter2=10):
        # try:
        csv_list = []
        for i in range(maxyear):
            self.simulateYear(iter1, iter2)
            self.currentboard.placeAllUnits()
            # self.currentboard.printGraph()
            score = {}
            for i in self.currentboard.countries:
                score[i.name] = i.getScore()
            with open('year_by_year.csv','a') as file:
                writer = csv.writer(file)
                writer.writerow([self.currentboard.year-1]+list(score.values()))
            for i in self.currentboard.countries:
                if i.score >= 18:
                    return i.name
        return "draw"
        # except Exception as e:
        #     print(e)
        #     self.currentboard.printGraph()
        #     breakpoint()

    def bulkSimulateGames(board, ngames=100, maxyear=15, iter1=10, iter2=10):
        file = 'year_by_year.csv'
        if(os.path.exists(file) and os.path.isfile(file)):
            os.remove(file)
        with open(file, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["year", "austria", "turkey", "italy", "france", "germany", "england", "russia"])
            writer.writeheader()
        start = time.time()
        results = {}
        csv_list = []
        for i in range(ngames):
            start2 = time.time()
            s = Simulation(board)
            res = s.simulateGame(maxyear, iter1, iter2)
            score = {}
            for j in s.currentboard.countries:
                score[j.name] = j.getScore()
            csv_list.append(score)

            try:
                results[res] += 1/ngames
            except:
                results[res] = 1/ngames

            end2 = time.time()
            print(i+1, "/", ngames, results, end2-start2, end2-start)

        end = time.time()
        print(end - start)

        with open("results.csv", mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=score.keys())
            writer.writeheader()  # Write header row
            writer.writerows(csv_list)