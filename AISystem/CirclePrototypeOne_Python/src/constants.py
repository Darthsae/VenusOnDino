from .world.tile import TileType, PhysicalState
from .living_entity import Species
from .ecs import ECSCoordinator, component
from .ai.evaluator import IEvaluator, EvaluatorInstance
from .ai.evaluators import TargetEvaluator
from .components.diet_component import NutrientType
from .texture_data import TextureData
from pygame import Surface

textures: list[TextureData] = []

tile_types: list[TileType] = [
    TileType("Dirt", (168, 84, 0), PhysicalState.SOLID),
    TileType("Water", (0, 0, 200), PhysicalState.LIQUID),
    TileType("Air", (255, 255, 255), PhysicalState.GAS)
]

species_types: list[Species] = [
    Species("Test", (0, 255, 255), 0, 1, 10, 50, 2, 10, 0, 0, {(NutrientType.PROTEIN, 2.5)}, {}, [
        EvaluatorInstance(0, {})
    ]),
    Species("Shrub", (0, 255, 0), 1, 2, 2, 50, 0, 0, 5, 0.1, {(NutrientType.PROTEIN, 2.5)}, {}, [])
]

evaluator_types: list[IEvaluator] = [
    TargetEvaluator()
]

METERS_PER_TILE: int = 2
PIXELS_PER_METER: int = 8
PIXELS_PER_TILE: int = METERS_PER_TILE * PIXELS_PER_METER

POSITION_COMPONENT: component
PHYSICAL_BODY_COMPONENT: component
SMELL_COMPONENT: component
TEXTURED_COMPONENT: component
SPECIES_COMPONENT: component
BRAIN_COMPONENT: component
SIGHT_COMPONENT: component
WORKING_MEMORY_COMPONENT: component
ASSOSCIATIVE_MEMORY_COMPONENT: component
DIET_COMPONENT: component
HEALTH_COMPONENT: component
MOVE_TO_TARGET_COMPONENT: component
GROWTH_COMPONENT: component
NUTRIENT_SOURCE_COMPONENT: component