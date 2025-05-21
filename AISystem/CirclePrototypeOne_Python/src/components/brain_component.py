from dataclasses import dataclass
from enum import Enum
from ..position import Point3D
from ..ecs import entity
from ..ai.evaluator import EvaluatorInstance

class PositionContext(Enum):
    SAFETY = 0
    FOOD = 1
    FIGHT = 2
    ROAM = 3
    MATE = 4

@dataclass
class TargetPosition:
    position: Point3D
    context: PositionContext
    valid: bool = False

    def setPosition(self, position: Point3D, context: PositionContext):
        self.position = position
        self.context = context
        self.valid = True
    
    def invalidate(self):
        self.valid = False

@dataclass
class BrainComponent:
    evaluators: list[EvaluatorInstance]
    entities: set[tuple[Point3D, entity]]
    target_position: TargetPosition
