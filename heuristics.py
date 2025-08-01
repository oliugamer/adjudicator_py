from metrics import Metrics
from board import Board
import itertools
from orders import Move, Hold, Support, Convoy
import math

class Heuristics:
    def __init__(self, board):
        self.board = board
        self.metrics = Metrics(board)

    def evaluatePosition(self, country):
        pass


class ScoreboardOnly(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        return country.getScore()

class Adjusments(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        return country.getAdjustments()

class UnitsOnly(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        nunits = len(country.units)
        h = 0

        for i in self.board.countries:
            h += (nunits-len(i.units))/nunits

        return h
    
class UnitUtility(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        score = 0
        for i in country.units:
            utility, _ = self.metrics.unitUtility(i)
            score += utility

        return score
    
class CloseThreats(Heuristics):
    def __init__(self, board):
        super().__init__(board)
    
    def evaluatePosition(self, country):
        close_units, close_countries = self.metrics.closeEnemyUnits(country)
        if len(close_countries) == 0:
            return 0
        return close_units/len(close_countries)
    
class GuaranteedSC(Heuristics):
    def __init__(self, board):
        super().__init__(board)
    
    def evaluatePosition(self, country):
        h = self.metrics.guaranteedSCs(country)
        return h

class CompleteH1(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        h1 = ScoreboardOnly(self.board)
        h2 = Adjusments(self.board)
        h3 = UnitsOnly(self.board)
        h4 = UnitUtility(self.board)
        h5 = CloseThreats(self.board)
        h6 = GuaranteedSC(self.board)

        score = h1.evaluatePosition(country) + \
                h2.evaluatePosition(country) + \
                h3.evaluatePosition(country) + \
                h4.evaluatePosition(country) + \
                h5.evaluatePosition(country) + \
                h6.evaluatePosition(country)

        return score
    
class CompleteH2(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluatePosition(self, country):
        h1 = ScoreboardOnly(self.board)
        h2 = Adjusments(self.board)
        h3 = UnitsOnly(self.board)
        h4 = UnitUtility(self.board)
        h5 = CloseThreats(self.board)
        h6 = GuaranteedSC(self.board)

        score = h1.evaluatePosition(country)*0.5 + \
                h2.evaluatePosition(country)*5 + \
                h3.evaluatePosition(country)*1 + \
                h4.evaluatePosition(country)*0.5 + \
                h5.evaluatePosition(country)*(-0.5) + \
                h6.evaluatePosition(country)*2

        return score

class LookAhead(Heuristics):
    def __init__(self, board):
        super().__init__(board)
    
    def evaluatePosition(self, country):
        # provinces = country.getFoWvision()
        # units = []
        # for i in provinces:
        #     if i.unit is not None:
        #         units.append(i)

        units = []
        for i in self.board.nodes:
            if i.unit is not None:
                units.append(i)

        orders = []
        a = []
        for i in units:
            aux = i.getAllLegalMoves()
            a.append(len(aux))
            orders.append(i.getAllLegalMoves())

        print(math.prod(a))
        # n = 0
        # for orderset in itertools.product(*orders):
        #     n+=1
        # print(n)

        # mean = 0
        # for orderset in itertools.product(*orders):
        #     newboard = Board.createBoardFromFile('initialmap.txt')
        #     newboard.importBoardState("units.txt")

        #     for i in orderset:
        #         match i[0]:
        #             case "m":
        #                 ordering_unit = newboard.getNode(i[1])
        #                 destination = newboard.getNode(i[2])
        #                 order = Move(ordering_unit, destination)
        #             case "h":
        #                 ordering_unit = newboard.getNode(i[1])
        #                 order = Hold(ordering_unit)
        #             case "sh":
        #                 ordering_unit = newboard.getNode(i[1])
        #                 destination = newboard.getNode(i[2])
        #                 order = Support(ordering_unit, Hold(destination, add_order=False))
        #             case "sa":
        #                 ordering_unit = newboard.getNode(i[1])
        #                 moving_unit = newboard.getNode(i[2])
        #                 destination = newboard.getNode(i[3])
        #                 order = Support(ordering_unit, Move(moving_unit, destination, add_order=False))
        #             case "c":
        #                 ordering_unit = newboard.getNode(i[1])
        #                 moving_unit = newboard.getNode(i[2])
        #                 destination = newboard.getNode(i[3])
        #                 order = Convoy(ordering_unit, Move(moving_unit, destination, add_order=False))
        #         newboard.addRawOrder(order)

        #     newboard.adjudicate()
        #     newboard.adjudicate() # no retreats phase
        #     h = CompleteH2(newboard)
        #     mean += h.evaluatePosition(country)
        
        # return mean/n

class SimHeuristic(Heuristics):
    def __init__(self, board):
        super().__init__(board)

    def evaluateSpring(self, country):
        val = 0
        for i in country.units:
            node = i.node
            if node.core and node.owned_by != country:
                val += 2
            enemyu = 0
            allyu = 0
            nearsc = 0
            nearemptysc = 0
            for j in node.getUniqueAdjacencies():
                if j.unit is not None:
                    if j.unit.owner == country:
                        allyu += 1
                    else:
                        enemyu += 1

                if j.core and j.owned_by != country:
                    nearsc += 1
                    if j.owned_by is None:
                        nearemptysc += 1

            val += (allyu-enemyu)/3
            val += nearsc/2 + nearemptysc*5

        for i in country.provinces:
            if i.unit is not None and i.unit.owner != country:
                val -= 1
        return val
    
    def evaluateFall(self, country):
        val = 0
        for i in country.units:
            node = i.node
            enemyu = 0
            allyu = 0
            nearsc = 0
            for j in node.getUniqueAdjacencies():
                if j.unit is not None:
                    if j.unit.owner == country:
                        allyu += 1
                    else:
                        enemyu += 1

                if j.core and j.owned_by != country:
                    nearsc += 1

            val += (allyu-enemyu)/3
            val += nearsc/3

        nocores = 0
        for i in country.cores:
            if i not in country.provinces:
                nocores += 1

        val += country.getAdjustments()*2 - nocores

        return val

    def evaluatePosition(self, country):
        val = 0
        if self.board.phase == "fall":
            val = self.evaluateSpring(country)
        elif self.board.phase == "winter":
            val = self.evaluateFall(country)
        return val
