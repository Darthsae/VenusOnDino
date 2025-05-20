from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from pygame import Surface
from pygame.gfxdraw import filled_circle
from .. import constants
from ..components.physical_body import PhysicalBody

def senseSight(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        