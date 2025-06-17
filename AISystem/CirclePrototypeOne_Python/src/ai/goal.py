from abc import ABCMeta, abstractmethod
from ..world.terrain import Terrain
from ..ecs import ECSCoordinator, entity
from ..components.diet_component import NutrientStat
from ..components.energy_component import EnergyComponent
from ..components.brain_component import BrainComponent
from ..components.health_component import HealthComponent
from enum import Enum
from .. import constants

class GoalLevel(Enum):
    UNIMPORTANT = 0
    EVENTUALLY = 1
    KINDA = 2
    NORMAL = 3
    IMPORTANT = 4
    NOW = 5
    LIFE_OR_DEATH = 6

class Goal(metaclass=ABCMeta):
    def __init__(self):
        self.value: float
        self.rank: int
    
    @abstractmethod
    def evaluate(self, coordinator: ECSCoordinator, terrain: Terrain, entity_id: entity, brain: BrainComponent, data: dict[str]) -> tuple[float, int]:
        ...

class SleepGoal(Goal):
    def __init__(self, energy: EnergyComponent):
        self.energy = energy
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        inverse_value: float = ((self.energy.max - self.energy.current) / self.energy.max)
        urgency: int = self.energy.current / 5
        return inverse_value / urgency, (GoalLevel.LIFE_OR_DEATH if inverse_value > 0.9 else (GoalLevel.IMPORTANT if inverse_value > 0.75 else (GoalLevel.KINDA if inverse_value > 0.25 else GoalLevel.UNIMPORTANT))).value

class BreedGoal(Goal):
    def __init__(self):
        ...
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        return 1, (GoalLevel.EVENTUALLY).value
        
class RoamGoal(Goal):
    def __init__(self):
        ...
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        return 1, 0

class NutritionGoal(Goal):
    def __init__(self, nutrition: NutrientStat):
        self.nutrition = nutrition
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        remaining: float = self.nutrition.current - self.nutrition.minimum
        relative: float = (remaining) / (self.nutrition.maximum - self.nutrition.minimum)
        inverse_relative: float = 1 - relative
        time_left: float = remaining / self.nutrition.consume

        if relative < 0:
            return -time_left * 1000, (GoalLevel.NOW).value
        
        return 1000 / time_left, (GoalLevel.IMPORTANT if inverse_relative < 0.25 else (GoalLevel.NORMAL if inverse_relative < 0.6 else (GoalLevel.KINDA if inverse_relative < 0.8 else GoalLevel.UNIMPORTANT))).value

class FleeGoal(Goal):
    def __init__(self, attacker: entity):
        self.attacker = attacker
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        if self.attacker not in coordinator.entities:
            return 0, 0
        health: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        value: float = (health.max - health.current) / health.max
        return data["low_health"] * (value) + data["full_health"] * (1 - value), (GoalLevel.KINDA).value

class ScavengeGoal(Goal):
    def __init__(self):
        ...
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        health: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        value: float = (health.max - health.current) / health.max
        return data["low_health"] * (value) + data["full_health"] * (1 - value), (GoalLevel.KINDA).value
    
class HuntGoal(Goal):
    def __init__(self):
        ...
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        health: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        value: float = (health.max - health.current) / health.max
        return data["low_health"] * (value) + data["full_health"] * (1 - value), (GoalLevel.KINDA).value

class DefendGoal(Goal):
    def __init__(self, attacker: entity):
        self.attacker = attacker
    
    def evaluate(self, coordinator, terrain, entity_id, brain, data):
        if self.attacker not in coordinator.entities:
            return 0, 0
        health: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        value: float = (health.max - health.current) / health.max
        return data["low_health"] * (value) + data["full_health"] * (1 - value), (GoalLevel.KINDA).value

#class SparGoal(Goal):
#    def __init__(self):
#        ...
#    
#    def evaluate(self, coordinator, terrain, entity_id, brain):
#        inverse_value: float = (1 - self.energy_percent)
#        urgency: int = self.time_remaining
#        return  inverse_value / urgency