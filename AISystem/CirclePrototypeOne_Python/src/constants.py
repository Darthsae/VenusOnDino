from .world.tile import TileType, PhysicalState
from .species import Species
from .ecs import component
from .ai.evaluator import EvaluatorInstance
from .ai.evaluators import sizeThreatEvaluator, foodEvaluator, componentEvaluator, attackThreatEvaluator
from .components.diet_component import NutrientType, NutrientStat
from .texture_data import TextureData
from .components.nutrient_source import NutrientSource
from .components.textured_component import TexturedComponent
from .components.timer_component import TimerComponent

textures: list[TextureData] = []


male: TextureData
female: TextureData
jungle: TextureData

nom_nom: TextureData
sleepy: TextureData
thirst_trap: TextureData
boot_coprolite: TextureData
warfare: TextureData

tile_types: list[TileType] = [
    TileType("Dirt", (236, 184, 138), TextureData.load("../../Assets/Textures/PixelArt/TopDown/Dirt.png"), PhysicalState.SOLID, [
        #("soil_source", 1.0),
    ]),
    TileType("Water", (36, 150, 210), TextureData.load("../../Assets/Textures/PixelArt/TopDown/Water.png"), PhysicalState.LIQUID, [
        ("nutrient_source", NutrientSource({NutrientType.WATER: 200})),
    ]),
    TileType("Air", (255, 255, 255), None, PhysicalState.GAS)
]

species_types: list[Species] = [
    Species("Goat", (0, 255, 255), 0, 0.85, 220, 500, 1, 10, 0.25, 0, 0, {NutrientType.PROTEIN: 200}, [
        NutrientStat(NutrientType.FIBER, 0.1, 12.0, 0.015, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.001, 30.0)
    ], 10, 0.1, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {}),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True),
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 1200, 1200, (1.5, 0, 1, 60, -160, 25, 0.01, 1), 5, 0, 0),
    Species("Shrub", (0, 255, 0), 2, 2, 2, 800, 0, 0, 0, 0.1, 0.001, {NutrientType.FIBER: 125, NutrientType.VITAMIN: 125}, [], -1, 0, True, [
        "health",
        "size_health",
        "growth",
        "remove_health",
        "reproduce"
    ], [], [
        ("remove_entity", True)
    ], 0, 0, (12.5, 1, 1, 60, -160, 0, 0.045, -1), 0, 0.0001, 1),
    Species("Tyrant", (155, 0, 0), 1, 6.5, 11000, 750, 1, 10, 1.6, 0, 0, {NutrientType.PROTEIN: 225}, [
        NutrientStat(NutrientType.PROTEIN, 0.1, 300.0, 0.005, 25),
        NutrientStat(NutrientType.WATER, 0.01, 150.0, 0.001, 15)
    ], 15, 0.75, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {"modifier": 350000000}),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {"modifier": 1.0 / 350000000})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True)
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 6000, 6000, (1.5, 2, 1, 120, -120, 25, 0.01, 1), 50, 0, 0),
    Species("Trumpet", (0, 255, 255), 5, 8, 8000, 450, 1, 10, 0.25, 0, 0, {NutrientType.PROTEIN: 250}, [
        NutrientStat(NutrientType.FIBER, 0.1, 25.0, 0.025, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.001, 30.0)
    ], 10, 0.5, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {}),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True),
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 1800, 1800, (1.5, 3, 4, 120, -180, 25, 0.01, 1), 10, 0, 0),
    Species("Tree", (0, 255, 0), 6, 3.5, 2, 2600, 0, 0, 0, 0.5, 0.001, {NutrientType.FIBER: 250}, [], -1, 0, True, [
        "health",
        "size_health",
        "growth",
        "remove_health",
        "reproduce"
    ], [], [
        ("remove_entity", True)
    ], 0, 0, (12.5, 4, 1, 60, -260, 0, 0.045, -1), 0, 0.0025, 1),
    Species("Bladehands", (0, 255, 255), 7, 5, 5000, 550, 1, 10, 0.25, 0, 0, {NutrientType.PROTEIN: 250}, [
        NutrientStat(NutrientType.FIBER, 0.1, 25.0, 0.025, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.001, 30.0)
    ], 10, 0.5, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {}),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True),
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 1800, 1800, (1.5, 5, 4, 120, -180, 25, 0.01, 1), 75, 0, 0),
    Species("Titan", (0, 255, 255), 8, 15, 90000, 1450, 1, 10, 2.5, 0, 0, {NutrientType.PROTEIN: 250}, [
        NutrientStat(NutrientType.FIBER, 0.1, 259.0, 0.025, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 390.0, 0.001, 30.0)
    ], 200, 2.5, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {}),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True),
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 1800, 1800, (1.5, 3, 4, 120, -180, 25, 0.01, 1), 10, 0, 0),
    Species("Vermin", (0, 255, 255), 9, 1.5, 25, 75, 13, 10, 0.25, 0, 0, {NutrientType.PROTEIN: 200}, [
        NutrientStat(NutrientType.PROTEIN, 0.1, 12.0, 0.015, 0.25),
        NutrientStat(NutrientType.VITAMIN, 0.1, 2.0, 0.001, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.001, 30.0)
    ], 10, 0.1, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy",
        "reproduce",
        "attack_target"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(3, {"modifier": 350000000}),
        EvaluatorInstance(0, {"modifier": 350000000}),
        EvaluatorInstance(1, {})
    ], [
        ("textured", TexturedComponent(3)),
        ("physical_buzz", ([
            "textured"
        ], [
            ("remove_entity", True),
        ])),
        ("timer", TimerComponent(0, 720, [], [
            ("textured", TexturedComponent(4))
        ]))
    ], 1200, 1200, (1.5, 0, 1, 60, -160, 25, 0.01, 1), 2, 0, 0),
]

evaluator_types: list = [
    sizeThreatEvaluator,
    foodEvaluator,
    componentEvaluator,
    attackThreatEvaluator
]

METERS_PER_TILE: int = 2
PIXELS_PER_METER: int = 24
PIXELS_PER_TILE: int = METERS_PER_TILE * PIXELS_PER_METER

def componentPull(id: str):
    match id:
        case "position":
            return POSITION_COMPONENT
        case "physical_body":
            return PHYSICAL_BODY_COMPONENT
        case "smell":
            return SMELL_COMPONENT
        case "textured":
            return TEXTURED_COMPONENT
        case "species":
            return SPECIES_COMPONENT
        case "brain":
            return BRAIN_COMPONENT
        case "sight":
            return SIGHT_COMPONENT
        case "working_memory":
            return WORKING_MEMORY_COMPONENT
        case "assosciative_memory":
            return ASSOSCIATIVE_MEMORY_COMPONENT
        case "diet":
            return DIET_COMPONENT
        case "health":
            return HEALTH_COMPONENT
        case "move_to_target":
            return MOVE_TO_TARGET_COMPONENT
        case "growth":
            return GROWTH_COMPONENT
        case "nutrient_source":
            return NUTRIENT_SOURCE_COMPONENT
        case "soil_source":
            return SOIL_SOURCE_COMPONENT
        case "soil_needer":
            return SOIL_NEEDER_COMPONENT
        case "eat_target":
            return EAT_TARGET_COMPONENT
        case "size_health":
            return SIZE_HEALTH_COMPONENT
        case "remove_health":
            return REMOVE_HEALTH_COMPONENT
        case "remove_entity":
            return REMOVE_ENTITY_COMPONENT
        case "dirty_position":
            return DIRTY_POSITION_COMPONENT
        case "add_health":
            return ADD_HEALTH_COMPONENT
        case "physical_buzz":
            return PHYSICAL_BUZZ_COMPONENT
        case "energy":
            return ENERGY_COMPONENT
        case "damaged":
            return DAMAGED_COMPONENT
        case "timer":
            return TIMER_COMPONENT
        case "reproduce":
            return REPRODUCE_COMPONENT
        case "attack_target":
            return ATTACK_TARGET_COMPONENT

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
SOIL_SOURCE_COMPONENT: component
SOIL_NEEDER_COMPONENT: component
EAT_TARGET_COMPONENT: component
SIZE_HEALTH_COMPONENT: component
REMOVE_HEALTH_COMPONENT: component
REMOVE_ENTITY_COMPONENT: component
DIRTY_POSITION_COMPONENT: component
ADD_HEALTH_COMPONENT: component
PHYSICAL_BUZZ_COMPONENT: component
ENERGY_COMPONENT: component
DAMAGED_COMPONENT: component
TIMER_COMPONENT: component
REPRODUCE_COMPONENT: component
ATTACK_TARGET_COMPONENT: component

DRAW_CIRCLES: bool = False
DRAW_SPRITES: bool = True
DRAW_TERRAIN: bool = True
DRAW_SIGHT: bool = False
DRAW_EMOTES: bool = True
DRAW_DIET: bool = True
RUNNING: bool = True
TAKE_STEP: bool = False

FPS: int = 60