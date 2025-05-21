from .world.tile import TileType, PhysicalState
from .species import Species
from .ecs import component
from .ai.evaluator import IEvaluator, EvaluatorInstance
from .ai.evaluators import targetEvaluator, foodEvaluator
from .components.diet_component import NutrientType, NutrientStat
from .texture_data import TextureData

textures: list[TextureData] = []

tile_types: list[TileType] = [
    TileType("Dirt", (168, 84, 0), PhysicalState.SOLID),
    TileType("Water", (0, 0, 200), PhysicalState.LIQUID),
    TileType("Air", (255, 255, 255), PhysicalState.GAS)
]

species_types: list[Species] = [
    Species("Test", (0, 255, 255), 0, 1, 10, 50, 2, 10, 0, 0, {NutrientType.PROTEIN: 2.5}, [
        NutrientStat(NutrientType.FIBER, 0.1, 3.0, 0.005, 0.25)
    ], 1, 0.1, False, [
        EvaluatorInstance(1, {})
    ]),
    Species("Shrub", (0, 255, 0), -1, 2, 2, 600, 0, 0, 5, 0.001, {NutrientType.FIBER: 25.5}, [], -1, 0, True, [])
]

evaluator_types: list[IEvaluator] = [
    targetEvaluator,
    foodEvaluator
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
EAT_TARGET_COMPONENT: component
SIZE_HEALTH_COMPONENT: component

DRAW_CIRCLES: bool = True
DRAW_SPRITES: bool = True
DRAW_TERRAIN: bool = True
RUNNING: bool = True
TAKE_STEP: bool = False

FPS: int = 60