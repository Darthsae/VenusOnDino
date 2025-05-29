from .ai.evaluator import EvaluatorInstance
from .components.diet_component import NutrientType, NutrientStat
from typing import Any

class Species:
    def __init__(self, name: str, color, texture: int, size: float, mass: float, max_life: int, speed: float, sight: float, sight_factor: float, growth_max_amount: float, growth_amount: float, nutrients: dict[NutrientType, float], diet: list[NutrientStat], eats: int, eat_amount: float, size_health: bool, remover: list[str], evaluators: list[EvaluatorInstance], adder: list[tuple[str, Any]], energy_max: int, energy: int, reproduction: None|tuple[float, int, int, int, int, int, float, bool] = None):
        self.name = name
        self.color = color
        self.texture = texture
        self.size = size
        self.mass = mass
        self.max_life = max_life
        self.speed = speed
        self.sight = sight
        self.sight_factor = sight_factor
        self.growth_max_amount = growth_max_amount
        self.growth_amount = growth_amount
        self.nutrients = nutrients
        self.diet = diet
        self.eats = eats
        self.eat_amount = eat_amount
        self.size_health = size_health
        self.remover = remover
        self.evaluators = evaluators
        self.adder = adder
        self.energy_max = energy_max
        self.energy = energy
        self.reproduction = reproduction