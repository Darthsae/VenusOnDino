from .tile import TileColumn
from ..octree import OctreeNode, Point3D

class Terrain:
    def __init__(self, size: int):
        self.columns: list[list[TileColumn]] = [[TileColumn() for _ in range(size)] for _ in range(size)]
        self.smells: OctreeNode = OctreeNode(Point3D(size // 2, size // 2, size // 2), size // 2)