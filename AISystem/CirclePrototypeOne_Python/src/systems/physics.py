from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from ..components.sight_sensor import SightSensor
from ..components.brain_component import BrainComponent
from .. import constants

def physics(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.SIGHT_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)