from .material import Material

class Substance:
    def __init__(self, material: Material):
        self.material = material