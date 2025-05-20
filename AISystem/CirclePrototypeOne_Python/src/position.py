from dataclasses import dataclass
from numbers import Complex

@dataclass(unsafe_hash=True)
class Point2D:
    x: int
    y: int

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
        if isinstance(other, (int, float)):
            return Point2D(self.x / other, self.y / other)

@dataclass(unsafe_hash=True)
class Point3D:
    x: int
    y: int
    z: int

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
        if isinstance(other, complex):
            return Point3D(self.x * other, self.y * other, self.z * other)
    
    def __floordiv__(self, other):
        if isinstance(other, complex):
            return Point3D(self.x / other, self.y / other, self.z / other)