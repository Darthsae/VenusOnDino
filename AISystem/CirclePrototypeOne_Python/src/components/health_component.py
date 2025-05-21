from dataclasses import dataclass

@dataclass
class HealthComponent:
    current: int
    max: int