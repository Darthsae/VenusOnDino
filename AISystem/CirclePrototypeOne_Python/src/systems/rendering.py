from ..ecs import ECSCoordinator, entity
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from pygame import Surface, Rect
from pygame.gfxdraw import filled_circle
from .. import constants
from ..components.brain_component import BrainComponent, CreatureState, Emoticon
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from ..components.diet_component import DietComponent, NutrientType
from ..components.health_component import HealthComponent
from ..components.energy_component import EnergyComponent
from ..texture_data import TextureData
import pygame, math

def renderTerrain(surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    top_left: Point2D = camera.asPoint2D() // constants.METERS_PER_TILE - terrain.position
    bottom_right: Point2D = (top_left - terrain.position + view_size // constants.PIXELS_PER_TILE)
    for y in range(int(max(top_left.y - 1, 0)), int(min(bottom_right.y + 1, Terrain.TERRAIN_SIZE))):
        for x in range(int(max(top_left.x - 1, 0)), int(min(bottom_right.x + 1, Terrain.TERRAIN_SIZE))):
            surface.fill(constants.tile_types[terrain.columns[y][x].topLayer().tile_type].color, ((x - camera.x / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, (y - camera.y / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE, constants.PIXELS_PER_TILE))

def renderTerrainTextures(surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain):
    top_left: Point2D = camera.asPoint2D() // constants.METERS_PER_TILE - terrain.position
    bottom_right: Point2D = (top_left - terrain.position + view_size // constants.PIXELS_PER_TILE)
    for y in range(int(max(top_left.y - 1, 0)), int(min(bottom_right.y + 1, Terrain.TERRAIN_SIZE))):
        for x in range(int(max(top_left.x - 1, 0)), int(min(bottom_right.x + 1, Terrain.TERRAIN_SIZE))):
            new_position = Point2D((x - camera.x / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE, (y - camera.y / constants.METERS_PER_TILE) * constants.PIXELS_PER_TILE)
            texture: TextureData = constants.tile_types[terrain.columns[y][x].topLayer().tile_type].texture
            scaling_factor: float = constants.PIXELS_PER_TILE / max(texture.rect.width, texture.rect.height)
            scaled_terrain_texture = pygame.transform.scale_by(texture.texture, scaling_factor)
            scaled_terrain_rect = Rect(int(new_position.x), int(new_position.y), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)
            surface.blit(scaled_terrain_texture, scaled_terrain_rect)

def renderCircles(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        scaling_factor = physical_body.size
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        filled_circle(surface, int(new_position.x), int(new_position.y), int(scaling_factor * constants.PIXELS_PER_METER), physical_body.color)

def renderSight(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        if coordinator.hasComponent(entity, constants.SIGHT_COMPONENT):
            physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
            sight: "SightSensor" = coordinator.getComponent(entity, constants.SIGHT_COMPONENT)
            
            angle: float = math.radians(270 - physical_body.rotation)
            offset: Point3D = Point3D(math.cos(angle), math.sin(angle), 0) * sight.distance * sight.offset_factor
            new_position = (position.asPoint2D() + offset  - camera) * constants.PIXELS_PER_METER
            filled_circle(surface, int(new_position.x), int(new_position.y), int(sight.distance * constants.PIXELS_PER_METER), (125, 125, 125, 25))
            brain: BrainComponent = coordinator.getComponent(entity, constants.BRAIN_COMPONENT)
            if brain.target_position.valid:
                move_position = (brain.target_position.position.asPoint2D() - camera) * constants.PIXELS_PER_METER
                filled_circle(surface, int(move_position.x), int(move_position.y), int(1 * constants.PIXELS_PER_METER), (25, 25, 25))

def renderTextures(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        if not coordinator.hasComponent(entity, constants.TEXTURED_COMPONENT):
            continue
        physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        texture_component: TexturedComponent = coordinator.getComponent(entity, constants.TEXTURED_COMPONENT)
        texture: TextureData = constants.textures[texture_component.texture_id]
        scaling_factor: float = constants.PIXELS_PER_METER / max(texture.rect.width, texture.rect.height) * physical_body.size * 2
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        rotated_entity_surface = pygame.transform.rotate(pygame.transform.scale_by(texture.texture, scaling_factor), physical_body.rotation)
        scaled_entity_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)
        rotated_entity_rect = rotated_entity_surface.get_rect()
        rotated_entity_rect.center = scaled_entity_rect.center
        if coordinator.hasComponent(entity, constants.DAMAGED_COMPONENT):
            tint_surface = Surface(rotated_entity_surface.size)
            tint_surface.fill(coordinator.getComponent(entity, constants.DAMAGED_COMPONENT))
            rotated_entity_surface.blit(tint_surface, special_flags=pygame.BLEND_MULT)
        surface.blit(rotated_entity_surface, rotated_entity_rect) 

def renderEmoticons(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, entities: set[tuple[Point3D, entity]]):
    for position, entity in (entities):
        if not coordinator.hasComponent(entity, constants.BRAIN_COMPONENT):
            continue
        brain: BrainComponent = coordinator.getComponent(entity, constants.BRAIN_COMPONENT)
        if brain.state == CreatureState.AWAKE and brain.emoticon == Emoticon.NONE:
            continue
        new_position = (position.asPoint2D() - camera) * constants.PIXELS_PER_METER

        if brain.state == CreatureState.SLEEPING:
            emoticon_texture_data: TextureData = constants.sleepy
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 4.0)
        elif brain.emoticon == Emoticon.EATING:
            emoticon_texture_data: TextureData = constants.nom_nom
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.DRINKING:
            emoticon_texture_data: TextureData = constants.thirst_trap
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.ROAMING:
            emoticon_texture_data: TextureData = constants.boot_coprolite
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        
        
        emoticon_rect = emoticon_texture.get_rect()
        emoticon_rect.center = (new_position.x, new_position.y - constants.PIXELS_PER_METER * 1.5)

        surface.blit(emoticon_texture, emoticon_rect)

def renderBar(surface: Surface, bar: Rect, percent: float, color):
    pixels_for_percent: float = bar.width * percent
    surface.fill(color, Rect(bar.topleft, (pixels_for_percent, bar.height)))
    surface.fill((12, 12, 12), Rect((bar.left + pixels_for_percent, bar.top), (bar.width - pixels_for_percent, bar.height)))

def renderBars(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, entities: set[tuple[Point3D, entity]]):
    for position, entity in (entities):
        if coordinator.hasComponent(entity, constants.DIET_COMPONENT) or coordinator.hasComponent(entity, constants.ENERGY_COMPONENT) or coordinator.hasComponent(entity, constants.HEALTH_COMPONENT):
            new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
            rect: Rect = Rect((0, 0), (1.5 * constants.PIXELS_PER_METER, 0.25 * constants.PIXELS_PER_METER))
            rect.centerx, rect.centery = new_position.x, new_position.y + 0.5 * constants.PIXELS_PER_METER
            if coordinator.hasComponent(entity, constants.HEALTH_COMPONENT):
                health: HealthComponent = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
                rect = rect.move(0, 0.3 * constants.PIXELS_PER_METER)
                renderBar(surface, rect, health.current / health.max, (200, 0, 0))
            if coordinator.hasComponent(entity, constants.ENERGY_COMPONENT):
                energy: EnergyComponent = coordinator.getComponent(entity, constants.ENERGY_COMPONENT)
                rect = rect.move(0, 0.3 * constants.PIXELS_PER_METER)
                renderBar(surface, rect, energy.current / energy.max, (180, 180, 0))
            if coordinator.hasComponent(entity, constants.DIET_COMPONENT):
                diet: DietComponent = coordinator.getComponent(entity, constants.DIET_COMPONENT)
                for nutrient_stat in diet.nutrients:
                    color = (0, 0, 0)
                    match nutrient_stat.nutrient:
                        case NutrientType.WATER:
                            color = (0, 0, 255)
                        case NutrientType.PROTEIN:
                            color = (128, 0, 0)
                        case NutrientType.FIBER:
                            color = (0, 200, 0)
                    rect = rect.move(0, 0.3 * constants.PIXELS_PER_METER)
                    renderBar(surface, rect, nutrient_stat.current / nutrient_stat.maximum, color)

        