from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Vector3D, Point3D
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.brain_component import BrainComponent
from .. import constants

def moveToTarget(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.MOVE_TO_TARGET_COMPONENT):
        move_to_target: MoveToTargetComponent = coordinator.getComponent(entity_id, constants.MOVE_TO_TARGET_COMPONENT)
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_position.valid:

            if brain_component.target_position.position == position:
                print("Noodle")

                continue

            step1 = brain_component.target_position.position - position

            step2 = step1.asVector3D()

            direction: Vector3D = step2.norm()

            coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + (direction * move_to_target.speed).asPoint3D())
