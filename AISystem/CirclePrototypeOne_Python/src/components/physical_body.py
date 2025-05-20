from dataclasses import dataclass

@dataclass
class PhysicalBody:
    mass: float
    size: float
    rotation: float = 0