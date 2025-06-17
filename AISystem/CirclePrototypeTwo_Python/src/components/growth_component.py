from dataclasses import dataclass

@dataclass
class GrowthComponent:
    amount: float
    max_amount: float
    current: float = 0