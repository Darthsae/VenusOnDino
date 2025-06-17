from dataclasses import dataclass

@dataclass
class PhysicalBody:
    mass: float
    size: float
    rotation: float = 0
    color: tuple[int, int, int] = (0, 0, 0)