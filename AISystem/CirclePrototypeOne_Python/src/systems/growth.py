from ..ecs import ECSCoordinator
from .. import constants
from ..components.growth_component import GrowthComponent
from ..components.physical_body import PhysicalBody

def growth(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.GROWTH_COMPONENT):
        growth_component: GrowthComponent = coordinator.getComponent(entity_id, constants.GROWTH_COMPONENT)
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        if growth_component.max_amount > growth_component.current:
            growth_component.current += growth_component.amount
            physical_body.size += growth_component.amount
            coordinator.setComponent(entity_id, constants.GROWTH_COMPONENT, growth_component)
            coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)