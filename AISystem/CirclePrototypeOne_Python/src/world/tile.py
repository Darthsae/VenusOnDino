from ..material import PhysicalState
from typing import NamedTuple
from ..texture_data import TextureData

class TileType:
    def __init__(self, name: str, color, texture: TextureData, state: PhysicalState, components: list = []):
        self.name = name
        self.color = color
        self.texture = texture
        self.state = state
        self.components = components


class ColumnLayerData(NamedTuple):
    tile_type: int
    height: float