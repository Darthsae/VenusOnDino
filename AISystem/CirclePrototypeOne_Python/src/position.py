from dataclasses import dataclass

@dataclass(unsafe_hash=True)
class Point3D:
    x: int
    y: int
    z: int