from dataclasses import dataclass
from enum import Enum

class NutrientType(Enum):
    PROTEIN: 0
    WATER: 1
    ELECTROLYTE: 2
    FIBER: 3
    VITAMIN: 4    

@dataclass
class NutrientStat:
    nutrient: NutrientType
    minimum: float
    maximum: float
    consume: float
    current: float

@dataclass
class DietComponent:
    nutrients: set[NutrientStat]