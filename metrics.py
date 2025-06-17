import units

class Metrics:
    def __init__(self, board):
        self.board = board

    def getUnitPossibleSCnocheck(self, unit):
        possible_sc = []
        match self.board.phase:
            case "spring":
                if type(unit) == units.Army:
                    adj = unit.node.getArmyAdjacencies()
                    possible_sc += adj
                    for i in adj:
                        for j in i.getArmyAdjacencies():
                            if j not in possible_sc:
                                possible_sc.append(j)

                elif type(unit) == units.Fleet:
                    adj = unit.node.getFleetAdjacencies()
                    possible_sc += adj
                    for i in adj:
                        for j in i.getFleetAdjacencies():
                            if j not in possible_sc:
                                possible_sc.append(j)
                
            case "fall": 
                if type(unit) == units.Army:
                    possible_sc = unit.node.getArmyAdjacencies()
                elif type(unit) == units.Fleet:
                    possible_sc = unit.node.getFleetAdjacencies()
        
        return possible_sc

    def getUnitPossibleSC(self, unit):
        possible_sc = self.getUnitPossibleSCnocheck(unit)

        scs = []
        for i in possible_sc:
            if i.core and i.owned_by != unit.owner:
                scs.append(i)
        return scs

    def unitUtility(self, unit):
        scs = self.getUnitPossibleSC(unit)
        
        occupied = 0
        score = len(scs)
        
        for i in scs:
            if i.unit is not None:
                occupied += 1

        return score, occupied
        
    def closeEnemyUnits(self, country):
        provinces = country.getLimitedVision()
        
        countries = []
        score = 0
        for i in provinces:
            if i.unit is not None and i.unit.owner != country:
                if i.unit.owner not in countries:
                    countries.append(i.unit.owner)
                score += 1
        
        return score, countries
    
    def guaranteedSCs(self, country):
        score = 0
        allpossiblesc = []
        for unit in country.units:
            for i in self.getUnitPossibleSC(unit):
                if i not in allpossiblesc:
                    allpossiblesc.append(i)
        
        for sc in allpossiblesc:
            isguaranteed = 0
            possible_units = []
            match self.board.phase:
                case "spring":
                    for i in sc.getUniqueAdjacencies():
                        if i not in possible_units and i.unit is not None:
                            possible_units.append(i)
                        for j in i.getUniqueAdjacencies():
                            if j not in possible_units and j.unit is not None:
                                possible_units.append(j)
                            
                case "fall": 
                    for i in sc.getUniqueAdjacencies():
                        if i.unit is not None:
                            possible_units.append(i)
            
            for i in possible_units:
                aux = self.getUnitPossibleSCnocheck(i.unit)
                if i.unit is not None and sc in aux:
                    if i.unit.owner == country:
                        isguaranteed += 1
                    else:
                        isguaranteed -= 1
            
            if isguaranteed > 0:
                score += 1
        
        return score

    
