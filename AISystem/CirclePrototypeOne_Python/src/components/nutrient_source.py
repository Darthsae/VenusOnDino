from dataclasses import dataclass
from .diet_component import NutrientType

@dataclass
class NutrientSource:
    nutrients: dict[NutrientType, float]

    def worthForNeeds(self, needs: list[tuple[NutrientType, float, float]]) -> float:
        return sum(map(self.func(), needs))
    
    def func(self):
        def funcy(tup):
            return tup[1] * tup[2] * self.nutrients.get(tup[0], 0)
        return funcy