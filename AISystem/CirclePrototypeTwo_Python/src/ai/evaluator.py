from dataclasses import dataclass
from typing import Any

@dataclass
class EvaluatorInstance:
    def __init__(self, evaluator_id: int, data: dict[str, Any]):
        self.evaluator_id = evaluator_id
        self.data = data