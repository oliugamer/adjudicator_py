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
        if node.owned_by is not None and node in node.owned_by.provinces:
            if node.owned_by != self:
                node.owned_by.provinces.remove(node)
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
    
    def __eq__(self, other):
        if other is None:
            return False
        return self.name == other.name

    def getLimitedVision(self):
        provinces = []
        for unit in self.units:
            for i in unit.node.getUniqueAdjacencies():
                if i not in provinces: 
                    provinces.append(i)
                for j in i.getUniqueAdjacencies():
                    if j not in provinces: 
                        provinces.append(j)
        
        return provinces

    def getFoWvision(self):
        provinces = []
        for unit in self.units:
            for i in unit.node.getUniqueAdjacencies():
                if i not in provinces: 
                    provinces.append(i)
        
        return provinces
    