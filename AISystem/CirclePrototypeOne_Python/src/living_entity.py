from .ai.evaluator import EvaluatorInstance

class Species:
    def __init__(self, name: str, color, size: float, mass: float, max_life: int, speed: float, sight: float, evaluators: list[EvaluatorInstance]):
        self.name = name
        self.color = color
        self.size = size
        self.mass = mass
        self.max_life = max_life
        self.speed = speed
        self.sight = sight
        self.evaluators = evaluators

class LivingEntity:
    def __init__(self):
        ...