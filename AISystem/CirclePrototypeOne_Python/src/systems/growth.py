from ..ecs import ECSCoordinator
from .. import constants
from ..components.growth_component import GrowthComponent
from ..components.physical_body import PhysicalBody

def growth(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.GROWTH_COMPONENT):
        growth_component: GrowthComponent = coordinator.getComponent(entity_id, constants.GROWTH_COMPONENT)
        if growth_component.max_amount > growth_component.current:
            physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
            growth_component.current += growth_component.amount
            physical_body.size += growth_component.amount
            coordinator.setComponent(entity_id, constants.GROWTH_COMPONENT, growth_component)
            coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)
        else:
            coordinator.removeComponents(entity_id, {constants.GROWTH_COMPONENT})
            if coordinator.hasComponent(entity_id, constants.REMOVE_HEALTH_COMPONENT):
                a: list[str] = coordinator.getComponent(entity_id, constants.REMOVE_HEALTH_COMPONENT)
                if "growth" in a:
                    a.remove("growth")