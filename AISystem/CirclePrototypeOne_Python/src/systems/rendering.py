from ..ecs import ECSCoordinator, entity
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from pygame import Surface, Rect
from pygame.gfxdraw import filled_circle
from .. import constants
from ..components.brain_component import BrainComponent, CreatureState, Emoticon
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from ..texture_data import TextureData
import pygame, math

def renderTerrain(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    top_left: Point2D = camera.asPoint2D() // constants.METERS_PER_TILE - terrain.position
    bottom_right: Point2D = (top_left - terrain.position + view_size // constants.PIXELS_PER_TILE)
    for y in range(int(max(top_left.y - 1, 0)), int(min(bottom_right.y + 1, Terrain.TERRAIN_SIZE))):
        for x in range(int(max(top_left.x - 1, 0)), int(min(bottom_right.x + 1, Terrain.TERRAIN_SIZE))):
            surface.fill(constants.tile_types[terrain.columns[y][x].topLayer().tile_type].color, ((x - camera.x / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, (y - camera.y / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE))

def renderTerrainTextures(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    top_left: Point2D = camera.asPoint2D() // constants.METERS_PER_TILE - terrain.position
    bottom_right: Point2D = (top_left - terrain.position + view_size // constants.PIXELS_PER_TILE)
    for y in range(int(max(top_left.y - 1, 0)), int(min(bottom_right.y + 2, Terrain.TERRAIN_SIZE))):
        for x in range(int(max(top_left.x - 1, 0)), int(min(bottom_right.x + 2, Terrain.TERRAIN_SIZE))):
            new_position = Point2D((x - camera.x / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, (y - camera.y / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE)
            texture: TextureData = constants.tile_types[terrain.columns[y][x].topLayer().tile_type].texture
            scaling_factor: float = constants.PIXELS_PER_TILE / max(texture.rect.width, texture.rect.height)
            newton = pygame.transform.scale_by(texture.texture, scaling_factor)
            new_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)

            surface.blit(newton, new_rect)

def renderCircles(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        physicalBody: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        scaling_factor = physicalBody.size
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        filled_circle(surface, int(new_position.x), int(new_position.y), int(scaling_factor * constants.PIXELS_PER_METER), physicalBody.color)

def renderSight(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        if coordinator.hasComponent(entity, constants.SIGHT_COMPONENT):
            physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
            sight: "SightSensor" = coordinator.getComponent(entity, constants.SIGHT_COMPONENT)
            
            angle: float = math.radians(270 - physical_body.rotation)
            offset: Point3D = Point3D(math.cos(angle), math.sin(angle), 0) * sight.distance * sight.offset_factor
            new_position = (position.asPoint2D() + offset  - camera) * constants.PIXELS_PER_METER
            filled_circle(surface, int(new_position.x), int(new_position.y), int(sight.distance * constants.PIXELS_PER_METER), (125, 125, 125, 125))

def renderTextures(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
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
        newton = pygame.transform.rotate(pygame.transform.scale_by(texture.texture, scaling_factor), physicalBody.rotation)
        new_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)
        narple = newton.get_rect()
        narple.center = new_rect.center
        if coordinator.hasComponent(entity, constants.DAMAGED_COMPONENT):
            tinter = Surface(newton.size)
            tinter.fill(coordinator.getComponent(entity, constants.DAMAGED_COMPONENT))
            newton.blit(tinter, special_flags=pygame.BLEND_MULT)
        surface.blit(newton, narple) 

def renderEmoticons(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
    for position, entity in (entities):
        if not coordinator.hasComponent(entity, constants.BRAIN_COMPONENT) or not coordinator.hasComponent(entity, constants.TEXTURED_COMPONENT):
            continue
        brain: BrainComponent = coordinator.getComponent(entity, constants.BRAIN_COMPONENT)
        if brain.state == CreatureState.AWAKE and brain.emoticon == Emoticon.NONE:
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
        
        if brain.state == CreatureState.SLEEPING:
            applicable: TextureData = constants.sleepy
            serf: Surface = pygame.transform.scale_by(applicable.texture, constants.PIXELS_PER_METER / max(applicable.rect.width, applicable.rect.height) * 4.0)
        elif brain.emoticon == Emoticon.EATING:
            applicable: TextureData = constants.hungy
            serf: Surface = pygame.transform.scale_by(applicable.texture, constants.PIXELS_PER_METER / max(applicable.rect.width, applicable.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.DRINKING:
            applicable: TextureData = constants.thirst_trap
            serf: Surface = pygame.transform.scale_by(applicable.texture, constants.PIXELS_PER_METER / max(applicable.rect.width, applicable.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.ROAMING:
            applicable: TextureData = constants.boot_coprolite
            serf: Surface = pygame.transform.scale_by(applicable.texture, constants.PIXELS_PER_METER / max(applicable.rect.width, applicable.rect.height) * 1.5)
        
        
        serf_rekt = serf.get_rect()
        serf_rekt.center =  (new_rect.centerx, new_rect.centery + constants.PIXELS_PER_METER / 12)

        surface.blit(serf, serf_rekt)