from ..material import PhysicalState
from typing import NamedTuple

class TileType:
    def __init__(self, name: str, color, state: PhysicalState, components: list = []):
        self.name = name
        self.color = color
        self.state = state
        self.components = components

class ColumnLayerData(NamedTuple):
    tile_type: int
    height: float