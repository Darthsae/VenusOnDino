from .position import Point2D

class QuadStruct:
    def __init__(self, position: Point2D, half_size: int, depth: int = 0):
        self.children: list[float] = [1 for _ in range(4)]
        self.position = position
        self.half_size = half_size
        self.depth = depth
        self.lower = self.position - Point2D.fromUniform(self.half_size)
        self.upper = self.position + Point2D.fromUniform(self.half_size)
    
    def query(self, point: Point2D) -> float:
        if (self.lower.x > point.x or
            self.upper.x < point.x or
            self.lower.y > point.y or
            self.upper.y < point.y):
            return 0
        
        x = int(point.x > self.position.x)
        y = int(point.y > self.position.y)
        return self.children[x + y * 2]
    
    def insert(self, point: Point2D, data: float):
        if (self.lower.x > point.x or
            self.upper.x < point.x or
            self.lower.y > point.y or
            self.upper.y < point.y):
            return 0
        
        x = int(point.x > self.position.x)
        y = int(point.y > self.position.y)
        self.children[x + y * 2] = data