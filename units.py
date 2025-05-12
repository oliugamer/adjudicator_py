import country
import graph

class Unit: 
    attacking_strength = 0

    def __init__(self, node: graph.Node, owner: country.Country):
        self.node = node
        self.owner = owner
        owner.units.append(self)
        node.addUnit(self)

class Army(Unit):
    def __init__(self, node, owner):
        super().__init__(node, owner)
    
    def __str__(self):
        return "Army"


class Fleet(Unit):
    def __init__(self, node, owner, coast = -1):
        super().__init__(node, owner)
        if type(node) == graph.MultipleCoastTile:
            node.unit_coast = coast

    def __str__(self):
        return "Fleet"
