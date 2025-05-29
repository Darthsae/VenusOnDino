from ..ecs import ECSCoordinator
from .. import constants
from ..components.health_component import HealthComponent
from ..components.physical_body import PhysicalBody
from ..components.timer_component import TimerComponent

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
                coordinator.setComponent(entity_id, constants.componentPull(comp), dat if comp != "timer" else TimerComponent(0, dat.time, dat.remove.copy(), dat.add.copy()))
            coordinator.removeComponents(entity_id, {constants.ADD_HEALTH_COMPONENT})

def updateRemoveEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT):
        #print(f"deleted {entity_id}")
        coordinator.removeEntity(entity_id)

def updateSizeEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.PHYSICAL_BUZZ_COMPONENT):
        phy: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        #print(f"{entity_id}")
        if phy.size <= 0:
            remove_component: list[str] = coordinator.getComponent(entity_id, constants.PHYSICAL_BUZZ_COMPONENT)[0]
            remover_component: list[tuple[str, ...]] = coordinator.getComponent(entity_id, constants.PHYSICAL_BUZZ_COMPONENT)[1]
            #print(f"marking {entity_id} for deletion")
            for comp, dat in remover_component:
                #print(f"removed {comp} {dat}")
                coordinator.setComponent(entity_id, constants.componentPull(comp), dat if comp != "timer" else TimerComponent(0, dat.time, dat.remove.copy(), dat.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.PHYSICAL_BUZZ_COMPONENT}) | set(map(constants.componentPull, remove_component)))