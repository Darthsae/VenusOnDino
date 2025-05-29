from dataclasses import dataclass
from numbers import Complex

@dataclass(unsafe_hash=True)
class Point2D:
    x: float
    y: float

    @classmethod
    def fromUniform(cls, value: float):
        return Point2D(value, value)
    
    def asPoint3D(self):
        return Point3D(self.x, self.y, 0)
    
    def __add__(self, other):
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point2D(self.x - other.x, self.y - other.y)
    
    def scaleBy(self, x: float, y: float):
        return Point2D(self.x * x, self.y * y)
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x * other, self.y * other)
        
    def __floordiv__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x / other, self.y / other)
        
    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x / other, self.y / other)
        
    def dist(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def distSQ(self, other) -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
    
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def norm(self) -> "Point2D":
        return self / self.magnitude()
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

@dataclass(unsafe_hash=True)
class Point3D:
    x: float
    y: float
    z: float

    @classmethod
    def fromUniform(cls, value: float):
        return Point3D(value, value, value)

    def asPoint2D(self):
        return Point2D(self.x, self.y)
    
    def __add__(self, other):
        if isinstance(other, Point3D):
            return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, Point2D):
            return Point3D(self.x + other.x, self.y + other.y, self.z)

    def __sub__(self, other):
        if isinstance(other, Point3D):
            return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, Point2D):
            return Point3D(self.x - other.x, self.y - other.y, self.z)
    
    def scaleBy(self, x: float, y: float, z: float):
        return Point3D(self.x * x, self.y * y, self.z * z)
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x * other, self.y * other, self.z * other)
    
    def __floordiv__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x / other, self.y / other, self.z / other)
    
    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x / other, self.y / other, self.z / other)
        
    def dist(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
    
    def distSQ(self, other) -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
    
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def norm(self) -> "Point3D":
        return self / self.magnitude()
    
    def __repr__(self):
        return f"({self.x}, {self.y}, {self.z})"