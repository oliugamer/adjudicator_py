from graph import *

class Country: 
    def __init__(self, name, cores = [], provinces = [], units = []):
        self.name = name
        self.cores = cores
        self.provinces = provinces
        self.units = units

    def addCore(self ,node: Node):
        self.cores.append(node)
        node.cored_by = self

    def addProvince(self, node: Node):
        self.provinces.append(node)
        node.owned_by = self

    def __str__(self):
        return self.name
    