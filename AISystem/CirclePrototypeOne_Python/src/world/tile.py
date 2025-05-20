from ..material import PhysicalState
from typing import NamedTuple

class TileType:
    def __init__(self, name: str, color, state: PhysicalState):
        self.name = name
        self.color = color
        self.state = state

class ColumnLayerData(NamedTuple):
    tile_type: int
    height: float

class TileColumn:
    def __init__(self):
        self.layers: list[ColumnLayerData] = []
    
    def topLayer(self) -> ColumnLayerData|None:
        from .. import constants
        for layer in reversed(self.layers):
            if constants.tile_types[layer.tile_type].state != PhysicalState.GAS:
                return layer
        return None