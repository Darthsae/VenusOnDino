from .position import Point3D

class OctreeNode[T]:
    MAX_OCCUPANTS: int = 32
    MAX_DEPTH: int = 8
    MAPPED: list[Point3D] = [
        Point3D(-1, -1, -1),
        Point3D( 1, -1, -1),
        Point3D(-1,  1, -1),
        Point3D( 1,  1, -1),
        Point3D(-1, -1,  1),
        Point3D( 1, -1,  1),
        Point3D(-1,  1,  1),
        Point3D( 1,  1,  1),
    ]

    def __init__(self, position: Point3D, half_size: int, depth: int = 0):
        self.children: list[OctreeNode|None] = [None for _ in range(8)]
        self.occupants: dict[Point3D, T] = {}
        self.position = position
        self.half_size = half_size
        self.depth = depth
    
    def query(self, lower_point: Point3D, higher_point: Point3D) -> set[tuple[Point3D, T]]:
        if (self.position.x - self.half_size > higher_point.x or
            self.position.x + self.half_size < lower_point.x or
            self.position.y - self.half_size > higher_point.y or
            self.position.y + self.half_size < lower_point.y or
            self.position.z - self.half_size > higher_point.z or
            self.position.z + self.half_size < lower_point.z):
            return set()
        elif self.children[0] == None:
            return {(pos, child) for pos, child in self.occupants.items() if (lower_point.x <= pos.x <= higher_point.x and
                                                          lower_point.y <= pos.y <= higher_point.y and
                                                          lower_point.z <= pos.z <= higher_point.z)}
        else:
            to_return = set()
            for child in self.children:
                to_return |= child.query(lower_point, higher_point)
            return to_return
    
    def insert(self, position: Point3D, data: T):
        if not (self.position.x - self.half_size <= position.x <= self.position.x + self.half_size and
                self.position.y - self.half_size <= position.y <= self.position.y + self.half_size and
                self.position.z - self.half_size <= position.z <= self.position.z + self.half_size):
            return
        elif self.children[0] == None:
            self.occupants[position] = data
            if len(self.occupants) == OctreeNode.MAX_OCCUPANTS and self.depth < OctreeNode.MAX_DEPTH:
                new_half = self.half_size // 2
                for i in range(8):
                    node_position: Point3D = Point3D(self.position.x, self.position.y, self.position.z) + OctreeNode.MAPPED[i] * new_half
                    self.children[i] = OctreeNode[T](node_position, new_half, self.depth + 1)
                for position2, occupant in self.occupants.items():
                    x = int(position2.x > self.position.x)
                    y = int(position2.y > self.position.y)
                    z = int(position2.z > self.position.z)
                    self.children[x + y * 2 + z * 4].insert(position2, occupant)
                self.occupants = {}
                return
        else:
            x = int(position.x > self.position.x)
            y = int(position.y > self.position.y)
            z = int(position.z > self.position.z)
            self.children[x + y * 2 + z * 4].insert(position, data)
    
    def pop(self, position: Point3D) -> bool:
        if not (self.position.x - self.half_size <= position.x <= self.position.x + self.half_size and
                self.position.y - self.half_size <= position.y <= self.position.y + self.half_size and
                self.position.z - self.half_size <= position.z <= self.position.z + self.half_size):
            return False
        elif self.children[0] == None:
            return self.occupants.pop(position, None) != None
        else:
            for child in self.children:
                if child.pop(position):
                    return True
            return False