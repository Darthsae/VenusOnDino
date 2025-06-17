from ..ecs import ECSCoordinator
from .. import constants
from ..position import Point3D
import random

def randomMovement(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + Point3D(random.randint(-1, 1), random.randint(-1, 1), 0))