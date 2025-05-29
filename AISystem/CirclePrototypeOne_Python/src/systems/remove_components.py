from ..ecs import ECSCoordinator
from .. import constants
from ..components.health_component import HealthComponent

def updateRemoveComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_HEALTH_COMPONENT):
        remove_component: list[str] = coordinator.getComponent(entity_id, constants.REMOVE_HEALTH_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            coordinator.removeComponents(entity_id, set(map(constants.componentPull, remove_component)))
                
def updateAddComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ADD_HEALTH_COMPONENT):
        remove_component: list[tuple[str, ...]] = coordinator.getComponent(entity_id, constants.ADD_HEALTH_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            for comp, dat in remove_component:
                coordinator.setComponent(entity_id, constants.componentPull(comp), dat)
            coordinator.removeComponents(entity_id, {constants.ADD_HEALTH_COMPONENT})

def updateRemoveEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT):
        coordinator.removeEntity(entity_id)