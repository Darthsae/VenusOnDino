from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from ..components.sight_sensor import SightSensor
from ..components.brain_component import BrainComponent
from .. import constants

def senseSight(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.SIGHT_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        sight_range: SightSensor = coordinator.getComponent(entity_id, constants.SIGHT_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        #print(entity_id)
        brain_component.entities = {(position, entity_id_iter) for position, entity_id_iter in terrain.entities.query(position - Point3D.fromUniform(sight_range.distance), position + Point3D.fromUniform(sight_range.distance)) if entity_id_iter != entity_id}
        #print(brain_component.entities)