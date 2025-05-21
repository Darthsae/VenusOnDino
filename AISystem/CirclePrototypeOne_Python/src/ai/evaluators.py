from .evaluator import IEvaluator, ECSCoordinator, entity, Any
from ..components.brain_component import BrainComponent, PositionContext
from ..components.diet_component import DietComponent, NutrientStat, NutrientType
from ..components.nutrient_source import NutrientSource
from .. import constants
from ..position import Point3D

class TargetEvaluator(IEvaluator):
    def evaluate(self, coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
        brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if len(brain.entities) > 0:
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            closest_point = sorted(brain.entities, key = lambda tup: position.distSQ(tup[0]))[0][0]
            brain.target_position.setPosition(closest_point, PositionContext.ROAM)

class FoodEvaluator(IEvaluator):
    def evaluate(self, coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
        brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
        listable = diet.orderedStats()
        print(listable)
        sorted_food = sorted([(tup[0], tup[1], coordinator.getComponent(tup[1], constants.NUTRIENT_SOURCE_COMPONENT).worthForNeeds(listable)) for tup in brain.entities if coordinator.hasComponent(tup[1], constants.NUTRIENT_SOURCE_COMPONENT) and coordinator.getComponent(tup[1], constants.NUTRIENT_SOURCE_COMPONENT).worthForNeeds(listable) > 0], key=lambda tup: tup[2], reverse=True)
        if len(sorted_food) > 0:
            brain.target_position.setPosition(sorted_food[0][0], PositionContext.FOOD)
            brain.target_creature.setCreature(sorted_food[0][1])
