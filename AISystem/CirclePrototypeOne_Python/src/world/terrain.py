from .tile import ColumnLayerData
from .tile_column import TileColumn
from ..octree import OctreeNode, Point3D
from ..position import Point2D
from ..ecs import ECSCoordinator, entity
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from ..components.health_component import HealthComponent
from ..components.brain_component import BrainComponent, EvaluatorInstance, TargetPosition, PositionContext, TargetCreature
from ..components.diet_component import DietComponent
from ..components.memory_component import MemoryComponent
from ..components.sight_sensor import SightSensor
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.nutrient_source import NutrientSource
from ..components.growth_component import GrowthComponent
from ..components.eat_target_component import EatTargetComponent
from .. import constants
import random

class Terrain:
    TERRAIN_SIZE: int = 100
    TERRAIN_HALF_SIZE: int = TERRAIN_SIZE // 2

    def __init__(self, position: Point2D):
        self.position = position
        self.columns: list[list[TileColumn]] = [[TileColumn() for _ in range(Terrain.TERRAIN_SIZE)] for _ in range(Terrain.TERRAIN_SIZE)]
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        self.smells: OctreeNode[Point2D] = OctreeNode[Point2D](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
    
    def regenerateEntityQuadtree(self, coordinator: ECSCoordinator):
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        for x in range(Terrain.TERRAIN_SIZE):
            for y in range(Terrain.TERRAIN_SIZE):
                column: TileColumn = self.columns[y][x]
                hot = column.getComponents()
                if len(hot) > 0:
                    quran = coordinator.createEntity()
                    for itex, idex in hot:
                        coordinator.setComponent(quran, constants.componentPull(itex), idex)
                    coordinator.setComponent(quran, constants.POSITION_COMPONENT, Point3D((x + 0.5) * constants.METERS_PER_TILE, (y + 0.5) * constants.METERS_PER_TILE, 10))
                    coordinator.setComponent(quran, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(100, constants.METERS_PER_TILE / 2))
        
        for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            self.entities.insert(position, entity_id)
        

    def updateDirtyEntityQuadtree(self, coordinator: ECSCoordinator):
        for entity_id in coordinator.getEntitiesWithComponent(constants.DIRTY_POSITION_COMPONENT):
            old_position: Point3D = coordinator.getComponent(entity_id, constants.DIRTY_POSITION_COMPONENT)
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            coordinator.removeComponents(entity_id, {constants.DIRTY_POSITION_COMPONENT})
            self.entities.pop(old_position)
            self.entities.insert(position, entity_id)

        for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT) & coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            self.entities.pop(position)

    def spoof(self):
        for y in range(Terrain.TERRAIN_SIZE):
            for x in range(Terrain.TERRAIN_SIZE):
                self.columns[y][x].layers = [ColumnLayerData(random.randint(0, 1), 0)]

    def addEntity(self, coordinator: ECSCoordinator, position: Point3D, species: int) -> entity:
        new_entity = coordinator.createEntity()
        coordinator.setComponent(new_entity, constants.POSITION_COMPONENT, position)
        coordinator.setComponent(new_entity, constants.SPECIES_COMPONENT, species)
        coordinator.setComponent(new_entity, constants.BRAIN_COMPONENT, BrainComponent(constants.species_types[species].evaluators.copy(), set(), TargetPosition(Point3D(0, 0, 0), PositionContext.ROAM), TargetCreature(0)))
        if constants.species_types[species].texture > -1:
            coordinator.setComponent(new_entity, constants.TEXTURED_COMPONENT, TexturedComponent(constants.species_types[species].texture))
        coordinator.setComponent(new_entity, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(constants.species_types[species].mass, constants.species_types[species].size))
        coordinator.setComponent(new_entity, constants.HEALTH_COMPONENT, HealthComponent(constants.species_types[species].max_life, constants.species_types[species].max_life))
        if constants.species_types[species].size_health:
            coordinator.setComponent(new_entity, constants.SIZE_HEALTH_COMPONENT, True)
        if constants.species_types[species].sight > 0:
            coordinator.setComponent(new_entity, constants.SIGHT_COMPONENT, SightSensor(constants.species_types[species].sight))
        if constants.species_types[species].speed > 0:
            coordinator.setComponent(new_entity, constants.MOVE_TO_TARGET_COMPONENT, MoveToTargetComponent(constants.species_types[species].speed))
        if constants.species_types[species].growth_amount > 0:
            coordinator.setComponent(new_entity, constants.GROWTH_COMPONENT, GrowthComponent(constants.species_types[species].growth_amount, constants.species_types[species].growth_max_amount))
        if len(constants.species_types[species].nutrients) > 0:
            coordinator.setComponent(new_entity, constants.NUTRIENT_SOURCE_COMPONENT, NutrientSource(constants.species_types[species].nutrients.copy()))
        if len(constants.species_types[species].diet) > 0:
            coordinator.setComponent(new_entity, constants.DIET_COMPONENT, DietComponent(constants.species_types[species].diet.copy()))
        if constants.species_types[species].eats > -1:
            coordinator.setComponent(new_entity, constants.EAT_TARGET_COMPONENT, EatTargetComponent(constants.species_types[species].eats, constants.species_types[species].eat_amount))
        if len(constants.species_types[species].remover) > 0:
            coordinator.setComponent(new_entity, constants.REMOVE_HEALTH_COMPONENT, constants.species_types[species].remover.copy())

        return new_entity