from ..ecs import ECSCoordinator
from .. import constants
from ..components.diet_component import DietComponent
from ..components.health_component import HealthComponent

def updateNutrients(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.DIET_COMPONENT):
        diet_component: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        for nutrient in diet_component.nutrients:
            nutrient.current = max(nutrient.current - nutrient.consume, 0)
            if nutrient.minimum < nutrient.current < nutrient.maximum:
                health_component.current = min(health_component.current + 1, health_component.max)
            else:
                health_component.current -= 1
                
