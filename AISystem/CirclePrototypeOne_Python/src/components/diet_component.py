from dataclasses import dataclass
from enum import Enum

class NutrientType(Enum):
    PROTEIN = 0
    WATER = 1
    ELECTROLYTE = 2
    FIBER = 3
    VITAMIN = 4    

@dataclass
class NutrientStat:
    nutrient: NutrientType
    minimum: float
    maximum: float
    consume: float
    current: float

@dataclass
class DietComponent:
    nutrients: list[NutrientStat]

    crucial: dict[NutrientType, bool] = None

    def orderedStats(self, amount: float) -> list[tuple[NutrientType, float, float, float]]:
        return sorted([(nutrient_stat.nutrient, ((nutrient_stat.maximum - nutrient_stat.minimum) - (nutrient_stat.current + amount - nutrient_stat.minimum)) * nutrient_stat.consume, nutrient_stat.consume, nutrient_stat.maximum - nutrient_stat.current - amount) for nutrient_stat in self.nutrients], key=lambda tup: tup[1])

    def updated(self, nutrient: "NutrientSource", amount: float) -> "DietComponent":
        return DietComponent([NutrientStat(instance.nutrient, instance.minimum, instance.maximum, instance.consume, instance.current + min(nutrient.nutrients.get(instance.nutrient, 0), amount)) for instance in self.nutrients])