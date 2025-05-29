from ..ecs import ECSCoordinator
from .. import constants
from ..components.diet_component import DietComponent
from ..components.health_component import HealthComponent
from ..components.energy_component import EnergyComponent
from ..components.brain_component import BrainComponent, CreatureState

def updateNutrients(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.DIET_COMPONENT):
        diet_component: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        change = 0
        for nutrient in diet_component.nutrients:
            nutrient.current = max(nutrient.current - nutrient.consume, 0)
            if nutrient.minimum <= nutrient.current <= nutrient.maximum and change >= 0:
                change += 1
            else:
                change = min(-1, change - 1)
        health_component.current = min(health_component.current + change, health_component.max)
                
def updateEnergy(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ENERGY_COMPONENT):
        energy_component: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        match brain_component.state:
            case CreatureState.SLEEPING:
                energy_component.current += 10
            case CreatureState.AWAKE:
                energy_component.current -= 1

def damagedComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.DAMAGED_COMPONENT):
        coordinator.removeComponents(entity_id, {constants.DAMAGED_COMPONENT})
