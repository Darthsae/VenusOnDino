from dataclasses import dataclass
from typing import Any

@dataclass
class Sex:
    MALE = 0
    FEMALE = 1
    OTHER = 2 # For the whatchma call it plants that have like 3 stages of reproduction.

@dataclass
class ReproduceComponent:
    sex: Sex
    offset: float
    species: int
    count: int
    delay: int 
    cooldown: int 
    energy_use: int
    chance: float
    others: int
    current: int = 0