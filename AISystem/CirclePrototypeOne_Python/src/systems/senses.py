from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point3D
from ..components.sight_sensor import SightSensor
from ..components.brain_component import BrainComponent, EntityTarget, PositionContext, Emoticon
from ..components.physical_body import PhysicalBody
from .. import constants
import math

def senseSight(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.SIGHT_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        sight_range: SightSensor = coordinator.getComponent(entity_id, constants.SIGHT_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_position.valid and brain_component.target_position.context == PositionContext.ROAM:
            brain_component.emoticon = Emoticon.ROAMING
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        angle: float = math.radians(270 - physical_body.rotation)
        rotation_offset: Point3D = Point3D(math.cos(angle), math.sin(angle), 0) * sight_range.distance * sight_range.offset_factor
        brain_component.entities = [EntityTarget(position, entity_id_iter) for position, entity_id_iter in terrain.entities.query(position + rotation_offset - Point3D.fromUniform(sight_range.distance), position + rotation_offset + Point3D.fromUniform(sight_range.distance)) if entity_id_iter != entity_id]