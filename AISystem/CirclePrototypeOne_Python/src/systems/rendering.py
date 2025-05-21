from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from pygame import Surface, Rect
from pygame.gfxdraw import filled_circle
from .. import constants
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from ..texture_data import TextureData
import pygame

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
        scaling_factor = physicalBody.size
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        filled_circle(surface, int(new_position.x), int(new_position.y), int(scaling_factor * constants.PIXELS_PER_METER), constants.species_types[coordinator.getComponent(entity, constants.SPECIES_COMPONENT)].color)

def renderTextures(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    entities = terrain.entities.query((camera.scaleBy(1, 1, 0) - terrain.position), (camera.scaleBy(1, 1, 0) + Point3D(view_size.x // constants.PIXELS_PER_METER, view_size.y // constants.PIXELS_PER_METER, terrain.TERRAIN_SIZE * constants.METERS_PER_TILE) - terrain.position))
    for position, entity in entities:
        if not coordinator.hasComponent(entity, constants.TEXTURED_COMPONENT):
            continue
        physicalBody: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        texture_component: TexturedComponent = coordinator.getComponent(entity, constants.TEXTURED_COMPONENT)
        texture: TextureData = constants.textures[texture_component.texture_id]
        scaling_factor: float = constants.PIXELS_PER_METER / max(texture.rect.width, texture.rect.height) * physicalBody.size * 2
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        new_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)
        surface.blit(pygame.transform.rotate(pygame.transform.scale_by(texture.texture, scaling_factor), physicalBody.rotation), new_rect) 