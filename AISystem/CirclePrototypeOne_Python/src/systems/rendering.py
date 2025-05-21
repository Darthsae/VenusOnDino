from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from pygame import Surface
from pygame.gfxdraw import filled_circle
from .. import constants
from ..components.physical_body import PhysicalBody

def renderTerrain(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    top_left: Point2D = camera.asPoint2D() // constants.METERS_PER_TILE - terrain.position
    bottom_right: Point2D = (top_left // constants.METERS_PER_TILE - terrain.position + view_size // constants.PIXELS_PER_TILE)
    surface.fill((16, 32, 168))
    for y in range(int(max(top_left.y, 0)), int(min(bottom_right.y, Terrain.TERRAIN_SIZE))):
        for x in range(int(max(top_left.x, 0)), int(min(bottom_right.x, Terrain.TERRAIN_SIZE))):
            surface.fill(constants.tile_types[terrain.columns[y][x].topLayer().tile_type].color, ((x - camera.x / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, (y - camera.y / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE))

def renderCircles(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    entities = terrain.entities.query((camera.scaleBy(1, 1, 0) - terrain.position), (camera.scaleBy(1, 1, 0) + Point3D(view_size.x // constants.PIXELS_PER_METER, view_size.y // constants.PIXELS_PER_METER, terrain.TERRAIN_SIZE * constants.METERS_PER_TILE) - terrain.position))
    for position, entity in entities:
        physicalBody: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        filled_circle(surface, int(new_position.x), int(new_position.y), int(physicalBody.size * constants.PIXELS_PER_METER), constants.species_types[coordinator.getComponent(entity, constants.SPECIES_COMPONENT)].color)
        