from .ai.evaluator import EvaluatorInstance
from .components.diet_component import NutrientType, NutrientStat

class Species:
    def __init__(self, name: str, color, texture: int, size: float, mass: float, max_life: int, speed: float, sight: float, growth_max_amount: float, growth_amount: float, nutrients: set[tuple[NutrientType, float]], diet: set[tuple[NutrientStat]], evaluators: list[EvaluatorInstance]):
        self.name = name
        self.color = color
        self.texture = texture
        self.size = size
        self.mass = mass
        self.max_life = max_life
        self.speed = speed
        self.sight = sight
        self.growth_max_amount = growth_max_amount
        self.growth_amount = growth_amount
        self.nutrients = nutrients
        self.diet = diet
        self.evaluators = evaluators

class LivingEntity:
    def __init__(self):
        ...