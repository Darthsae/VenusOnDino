from .evaluator import Any
from ..ecs import ECSCoordinator, entity, component
from ..components.brain_component import BrainComponent
from ..components.diet_component import DietComponent
from ..components.nutrient_source import NutrientSource, NutrientType
from ..components.physical_body import PhysicalBody
from ..components.attack_target_component import AttackTargetComponent
from ..components.health_component import HealthComponent
#from ..world.terrain import Terrain
from .. import constants
import math

#def targetEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
#    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
#    if len(brain.entities) > 0:
#        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
#        closest_point = sorted(brain.entities, key = lambda tup: position.distSQ(tup[0]))[0][0]
#        brain.target_position.setPosition(closest_point, PositionContext.ROAM)

VOLUME_OF_SPHERE: float = 4 / 3 * math.pi

def foodEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, _: dict[str, Any]):
    diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
    amount: float = 0.0
    if coordinator.hasComponent(entity_id, constants.EAT_TARGET_COMPONENT):
        amount = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT).amount

    listable = diet.orderedStats(amount)
    crucial_holder = set(diet.crucial.keys())
    for i, entity_instance in enumerate(brain.entities):
        if not coordinator.hasComponent(entity_instance.id, constants.NUTRIENT_SOURCE_COMPONENT):
            continue

        nutrient_source: NutrientSource = coordinator.getComponent(entity_instance.id, constants.NUTRIENT_SOURCE_COMPONENT)
        volume: float = (coordinator.getComponent(entity_instance.id, constants.PHYSICAL_BODY_COMPONENT).size ** 3) * VOLUME_OF_SPHERE
        nutrient_value = 0.0
        for nutrient_type, nutrient_need, nutrient_consumption, nutrient_new_value in listable:
            nutrient_density = nutrient_source.nutrients.get(nutrient_type, 0)
            if nutrient_density == 0:
                continue
            
            if nutrient_type in crucial_holder:
                nutrient_value += 10000 * nutrient_need * nutrient_density * volume
                diet.crucial[nutrient_type] = True
            elif nutrient_new_value < 0:
                nutrient_value = -1
                break
            else:
                nutrient_value += nutrient_need * nutrient_consumption * nutrient_density * volume
        brain.entities[i].nutrition = nutrient_value
    
    brain.must_roam = not any(crucial is True for crucial in diet.crucial.values()) and len(diet.crucial) > 0

def sizeThreatEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, data: dict[str, Any]):
    physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
    for i, entity_instance in enumerate(brain.entities):
        if brain.entities[i].threat != None:
            brain.entities[i].threat += (coordinator.getComponent(entity_instance.id, constants.PHYSICAL_BODY_COMPONENT).size - physical_body.size) * data.get("modifier", 1.0) * 10000

def attackThreatEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, data: dict[str, Any]):
    health: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
    for i, _ in enumerate(brain.entities):
        if brain.entities[i].threat != None and coordinator.hasComponent(brain.entities[i].id, constants.ATTACK_TARGET_COMPONENT):
            brain.entities[i].threat += (coordinator.getComponent(brain.entities[i].id, constants.ATTACK_TARGET_COMPONENT).damage / health.current) * data.get("modifier", 1.0) * 10000

def componentEvaluator(coordinator: ECSCoordinator, _: entity, brain: BrainComponent, data: dict[str, Any]):
    components: list[component] = map(constants.componentPull, data["threat"])
    for i, entity_eval in enumerate(brain.entities):
        for component_type in components:
            if coordinator.hasComponent(entity_eval.id, component_type):
                brain.entities[i].threat = 0.0
                break
