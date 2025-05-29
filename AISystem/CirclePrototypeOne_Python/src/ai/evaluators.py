from .evaluator import ECSCoordinator, entity, Any
from ..ecs import component
from ..components.brain_component import BrainComponent, PositionContext
from ..components.diet_component import DietComponent
from ..components.physical_body import PhysicalBody
from .. import constants
from ..position import Point3D

#def targetEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
#    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
#    if len(brain.entities) > 0:
#        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
#        closest_point = sorted(brain.entities, key = lambda tup: position.distSQ(tup[0]))[0][0]
#        brain.target_position.setPosition(closest_point, PositionContext.ROAM)

def foodEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
    diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
    amount: float = 0.0
    if coordinator.hasComponent(entity_id, constants.EAT_TARGET_COMPONENT):
        amount = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT).amount
        #print(amount)
    listable = diet.orderedStats(amount)
    for i, entity_eval in enumerate(brain.entities):
        if coordinator.hasComponent(entity_eval.id, constants.NUTRIENT_SOURCE_COMPONENT):
            brain.entities[i].nutrition = coordinator.getComponent(entity_eval.id, constants.NUTRIENT_SOURCE_COMPONENT).worthForNeeds(listable)

def sizeThreatEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
    physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
    for i, entity_eval in enumerate(brain.entities):
        if brain.entities[i].threat != None:
            brain.entities[i].threat += (coordinator.getComponent(entity_eval.id, constants.PHYSICAL_BODY_COMPONENT).size - physical_body.size) * data.get("modifier", 1.0)

def componentEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
    components: list[component] = map(constants.componentPull, data["threat"])
    for i, entity_eval in enumerate(brain.entities):
        for componenta in components:
            if coordinator.hasComponent(entity_eval.id, componenta):
                brain.entities[i].threat = 0.0
                break
