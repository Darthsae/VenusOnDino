from .tile import ColumnLayerData, PhysicalState
from .. import constants

class TileColumn:
    def __init__(self):
        self.layers: list[ColumnLayerData] = []
    
    def getComponents(self):
        to_return = []
        for layer in self.layers:
            to_return.extend(constants.tile_types[layer.tile_type].components)
        return to_return
    
    def topLayer(self) -> ColumnLayerData|None:
        for layer in reversed(self.layers):
            if constants.tile_types[layer.tile_type].state != PhysicalState.GAS:
                return layer
        return None