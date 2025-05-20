class Species:
    def __init__(self, name: str, color, size: float, mass: float):
        self.name = name
        self.color = color
        self.size = size
        self.mass = mass

class LivingEntity:
    def __init__(self):
        ...