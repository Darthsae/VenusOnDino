from dataclasses import dataclass
from typing import Any
from abc import ABC, abstractmethod
from ..ecs import ECSCoordinator, entity

@dataclass
class EvaluatorInstance:
    def __init__(self, evaluator_id: int, data: dict[str, Any]):
        self.evaluator_id = evaluator_id
        self.data = data

class IEvaluator(ABC):
    @abstractmethod
    def evaluate(self, coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
        pass