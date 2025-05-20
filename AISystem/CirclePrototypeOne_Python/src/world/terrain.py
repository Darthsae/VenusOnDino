from .tile import TileColumn, ColumnLayerData
from ..octree import OctreeNode, Point3D
from ..position import Point2D
from ..ecs import ECSCoordinator, entity
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from .. import constants
import random

class Terrain:
    TERRAIN_SIZE: int = 64
    TERRAIN_HALF_SIZE: int = TERRAIN_SIZE // 2

    def __init__(self, position: Point2D):
        self.position = position
        self.columns: list[list[TileColumn]] = [[TileColumn() for _ in range(Terrain.TERRAIN_SIZE)] for _ in range(Terrain.TERRAIN_SIZE)]
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        self.smells: OctreeNode[Point2D] = OctreeNode[Point2D](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
    
    def regenerateEntityQuadtree(self, coordinator: ECSCoordinator):
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            self.entities.insert(position, entity_id)

    def spoof(self):
        for y in range(Terrain.TERRAIN_SIZE):
            for x in range(Terrain.TERRAIN_SIZE):
                self.columns[y][x].layers = [ColumnLayerData(random.randint(0, 1), 0)]

    def addEntity(self, coordinator: ECSCoordinator, position: Point3D, species: int) -> entity:
        new_entity = coordinator.createEntity()
        coordinator.setComponent(new_entity, constants.POSITION_COMPONENT, position)
        coordinator.setComponent(new_entity, constants.SPECIES_COMPONENT, species)
        #coordinator.setComponent(new_entity, constants.TEXTURED_COMPONENT, )
        coordinator.setComponent(new_entity, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(constants.species_types[species].mass, constants.species_types[species].size))
        return new_entity