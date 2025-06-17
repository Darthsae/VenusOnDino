from .tile import ColumnLayerData
from .tile_column import TileColumn
from ..octree import OctreeNode, Point3D
from ..quad_struct import QuadStruct, Point2D
from ..position import Point2D
from ..ecs import ECSCoordinator, entity
from ..components.physical_body import PhysicalBody
from ..components.textured_component import TexturedComponent
from ..components.health_component import HealthComponent
from ..components.brain_component import BrainComponent, TargetPosition, PositionContext, TargetCreature
from ..components.diet_component import DietComponent
from ..components.sight_sensor import SightSensor
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.nutrient_source import NutrientSource
from ..components.growth_component import GrowthComponent
from ..components.eat_target_component import EatTargetComponent
from ..components.energy_component import EnergyComponent
from ..components.reproduce_component import ReproduceComponent, Sex
from ..components.attack_target_component import AttackTargetComponent
from .. import constants
import random, opensimplex, numpy

class Terrain:
    TERRAIN_SIZE: int = 100
    TERRAIN_HALF_SIZE: int = TERRAIN_SIZE // 2

    def __init__(self, position: Point2D):
        self.position = position
        self.columns: list[list[TileColumn]] = [[TileColumn() for _ in range(Terrain.TERRAIN_SIZE)] for _ in range(Terrain.TERRAIN_SIZE)]
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        self.tiles: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        self.smells: OctreeNode[Point2D] = OctreeNode[Point2D](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        self.soil: QuadStruct = QuadStruct(Point2D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)

    def regenerateEntityQuadtree(self, coordinator: ECSCoordinator):
        self.entities: OctreeNode[entity] = OctreeNode[entity](Point3D(Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE, Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE), Terrain.TERRAIN_HALF_SIZE * constants.METERS_PER_TILE)
        for x in range(Terrain.TERRAIN_SIZE):
            for y in range(Terrain.TERRAIN_SIZE):
                column: TileColumn = self.columns[y][x]
                tile_components = column.getComponents()
                if len(tile_components) > 0:
                    tile_entity = coordinator.createEntity()
                    for component_type, component_data in tile_components:
                        coordinator.setComponent(tile_entity, constants.componentPull(component_type), component_data)
                    coordinator.setComponent(tile_entity, constants.POSITION_COMPONENT, Point3D((x + 0.5) * constants.METERS_PER_TILE, (y + 0.5) * constants.METERS_PER_TILE, 2.5))
                    coordinator.setComponent(tile_entity, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(100, constants.METERS_PER_TILE / 2))
                    #self.tiles.insert(Point3D((x + 0.5) * constants.METERS_PER_TILE, (y + 0.5) * constants.METERS_PER_TILE, 2), tile_entity)
        
        for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            self.entities.insert(position, entity_id)
        

    def updateDirtyEntityQuadtree(self, coordinator: ECSCoordinator):
        for entity_id in coordinator.getEntitiesWithComponent(constants.DIRTY_POSITION_COMPONENT):
            old_position: Point3D = coordinator.getComponent(entity_id, constants.DIRTY_POSITION_COMPONENT)
            new_position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            coordinator.removeComponents(entity_id, {constants.DIRTY_POSITION_COMPONENT})
            self.entities.pop(old_position)
            #print(f"Moved {entity_id} from {old_position} to {new_position}")
            self.entities.insert(new_position, entity_id)

        for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT) & coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            #print(f"Removed {entity_id} from quadtree at {position} and it was a {boba}, nearby are: {self.entities.query(position - Point3D(1, 1, 1), position + Point3D(1, 1, 1))}")
            if not self.entities.pop(position):
                for position_next, entity_id_iter in self.entities.query(position - Point3D(1, 1, 1), position + Point3D(1, 1, 1)):
                    if entity_id_iter == entity_id:
                        self.entities.pop(position_next)
                        break
    def spoof(self):
        for y in range(Terrain.TERRAIN_SIZE):
            for x in range(Terrain.TERRAIN_SIZE):
                self.columns[y][x].layers = [ColumnLayerData(1 if (opensimplex.noise2(x * 0.07, y * 0.07) - 0.25 * opensimplex.noise2(25 + y * 0.15, 25 + x * 0.15)) > 0.125 else 0, 0)]

    def addEntity(self, coordinator: ECSCoordinator, position: Point3D, species: int) -> entity:
        new_entity = coordinator.createEntity()
        coordinator.setComponent(new_entity, constants.POSITION_COMPONENT, position)
        coordinator.setComponent(new_entity, constants.SPECIES_COMPONENT, species)
        if len(constants.species_types[species].evaluators) > 0:
            coordinator.setComponent(new_entity, constants.BRAIN_COMPONENT, BrainComponent(constants.species_types[species].evaluators.copy(), set(), TargetPosition(Point3D(0, 0, 0), PositionContext.ROAM), TargetCreature(0)))
        if constants.species_types[species].texture > -1:
            coordinator.setComponent(new_entity, constants.TEXTURED_COMPONENT, TexturedComponent(constants.species_types[species].texture))
        coordinator.setComponent(new_entity, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(constants.species_types[species].mass, constants.species_types[species].size))
        coordinator.setComponent(new_entity, constants.HEALTH_COMPONENT, HealthComponent(constants.species_types[species].max_life, constants.species_types[species].max_life))
        if constants.species_types[species].size_health:
            coordinator.setComponent(new_entity, constants.SIZE_HEALTH_COMPONENT, True)
        if constants.species_types[species].sight > 0:
            coordinator.setComponent(new_entity, constants.SIGHT_COMPONENT, SightSensor(constants.species_types[species].sight, constants.species_types[species].sight_factor))
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
        if len(constants.species_types[species].adder) > 0:
            coordinator.setComponent(new_entity, constants.ADD_HEALTH_COMPONENT, constants.species_types[species].adder.copy())
        if constants.species_types[species].energy_max > 0:
            coordinator.setComponent(new_entity, constants.ENERGY_COMPONENT, EnergyComponent(constants.species_types[species].energy, constants.species_types[species].energy_max))
        if constants.species_types[species].reproduction != None:
            reproduction_data = constants.species_types[species].reproduction
            a: Sex = Sex.OTHER
            if constants.species_types[species].typing == 1:
                a = Sex.FEMALE if random.random > 0.5 else Sex.MALE
            coordinator.setComponent(new_entity, constants.REPRODUCE_COMPONENT, ReproduceComponent(a, reproduction_data[0], reproduction_data[1], reproduction_data[2], reproduction_data[3], reproduction_data[4], reproduction_data[5], reproduction_data[6], reproduction_data[7]))
        if constants.species_types[species].damage > 0:
            coordinator.setComponent(new_entity, constants.ATTACK_TARGET_COMPONENT, AttackTargetComponent(constants.species_types[species].damage))
        if constants.species_types[species].soil > 0:
            coordinator.setComponent(new_entity, constants.SOIL_NEEDER_COMPONENT, constants.species_types[species].soil)
        return new_entity