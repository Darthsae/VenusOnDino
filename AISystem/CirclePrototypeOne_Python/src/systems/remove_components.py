from ..ecs import ECSCoordinator
from .. import constants
from ..components.health_component import HealthComponent
from ..components.physical_body import PhysicalBody
from ..components.timer_component import TimerComponent
from ..components.reproduce_component import ReproduceComponent
from ..world.terrain import Terrain
from ..position import Point3D
import random

def updateRemoveComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_HEALTH_COMPONENT):
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            remove_component: list[str] = coordinator.getComponent(entity_id, constants.REMOVE_HEALTH_COMPONENT)
            coordinator.removeComponents(entity_id, set(map(constants.componentPull, remove_component)))
                
def updateAddComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ADD_HEALTH_COMPONENT):
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            add_component: list[tuple[str, ...]] = coordinator.getComponent(entity_id, constants.ADD_HEALTH_COMPONENT)
            for component_type, component_data in add_component:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()) if component_type == "timer" else component_data)
            coordinator.removeComponents(entity_id, {constants.ADD_HEALTH_COMPONENT})

def updateRemoveEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT):
        #print(f"Deleted {entity_id}")
        coordinator.removeEntity(entity_id)

def updateSizeEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.PHYSICAL_BUZZ_COMPONENT):
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        if physical_body.size <= 0:
            physical_buzz = coordinator.getComponent(entity_id, constants.PHYSICAL_BUZZ_COMPONENT)
            for component_type, component_data in physical_buzz[1]:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), component_data if component_type != "timer" else TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.PHYSICAL_BUZZ_COMPONENT}) | set(map(constants.componentPull, physical_buzz[0])))