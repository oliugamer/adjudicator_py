import country
import graph

class Unit: 
    def __init__(self, node: graph.Node, owner: country.Country):
        self.node = node
        self.owner = owner
        owner.addUnit(self)
        node.addUnit(self)
        self.attacking_strength = 0
        self.order = None

class Army(Unit):
    def __init__(self, node, owner):
        super().__init__(node, owner)
    
    def __str__(self):
        return "Army, " + self.owner.name


class Fleet(Unit):
    def __init__(self, node, owner, coast = -1):
        self.coast = coast
        super().__init__(node, owner)
        if type(node) == graph.MultipleCoastTile:
            node.unit_coast = coast

    def __str__(self):
        return "Fleet, " + self.owner.name
