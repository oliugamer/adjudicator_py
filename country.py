from graph import Node

class Country: 
    def __init__(self, name, cores, provinces, units):
        self.name = name.lower()
        self.cores = cores
        self.provinces = provinces
        self.units = units
        self.score = len(cores)

    def addCore(self ,node: Node):
        self.cores.append(node)
        node.cored_by = self

    def addProvince(self, node: Node):
        self.provinces.append(node)
        node.owned_by = self

    def addUnit(self, unit):
        self.units.append(unit)

    def getScore(self):
        return len(self.provinces)
    
    def getAdjustments(self):
        return len(self.provinces) - len(self.units)

    def __str__(self):
        return self.name
    