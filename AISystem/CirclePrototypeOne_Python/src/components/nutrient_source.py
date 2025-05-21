from dataclasses import dataclass
from .diet_component import NutrientType

@dataclass
class NutrientSource:
    nutrients: set[tuple[NutrientType, float]]