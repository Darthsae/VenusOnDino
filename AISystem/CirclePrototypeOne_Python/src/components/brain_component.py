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

class CreatureContext(Enum):
    SAFETY = 0
    EAT = 1
    FIGHT = 2
    MATE = 3

@dataclass
class EntityTarget:
    position: Point3D
    id: entity
    threat: float = None
    nutrition: float = None

    def threatByDistance(self, point: Point3D):
        return (self.threat * abs(self.threat)) / (point.distSQ(self.position) if self.position != point else 1.0) if self.threat != None else 0.0

    def nutritionByDistance(self, point: Point3D):
        return self.nutrition / (point.distSQ(self.position) if self.position != point else 1.0) if self.nutrition != None else 0.0

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
class TargetCreature:
    creature: entity
    context: CreatureContext = CreatureContext.SAFETY
    valid: bool = False

    def setCreature(self, creature: entity, context: CreatureContext):
        self.creature = creature
        self.context = context
        self.valid = True

class CreatureState(Enum):
    AWAKE = 0
    SLEEPING = 1

class Emoticon(Enum):
    NONE = 0
    EATING = 1
    DRINKING = 2
    ROAMING = 3
    FIGHTING = 4

@dataclass
class BrainComponent:
    evaluators: list[EvaluatorInstance]
    entities: list[EntityTarget]
    target_position: TargetPosition
    target_creature: TargetCreature
    state: CreatureState = CreatureState.AWAKE
    emoticon: Emoticon = Emoticon.NONE
    must_roam: bool = False
    attacker: entity = -1
