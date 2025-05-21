from dataclasses import dataclass
from .diet_component import NutrientType
import math

@dataclass
class NutrientSource:
    nutrients: dict[NutrientType, float]

    def worthForNeeds(self, needs: list[tuple[NutrientType, float, float]]) -> float:
        value = 0
        for nutrient, need, modifier in needs:
            if nutrient in self.nutrients:
                value += abs(need * modifier * self.nutrients[nutrient])
        return value