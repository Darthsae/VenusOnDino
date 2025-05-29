from dataclasses import dataclass
from typing import Any

@dataclass
class ReproduceComponent:
    offset: float
    species: int
    count: int
    delay: int 
    energy_use: int
    chance: float
    others: bool
    current: int = 0