from .tile import ColumnLayerData, PhysicalState
from .. import constants

class TileColumn:
    def __init__(self):
        self.layers: list[ColumnLayerData] = []
    
    def topLayer(self) -> ColumnLayerData|None:
        for layer in reversed(self.layers):
            if constants.tile_types[layer.tile_type].state != PhysicalState.GAS:
                return layer
        return None