# Project Markup

## File Tree

```
./
    main.py
    __init__.py
    src/
        constants.py
        ecs.py
        material.py
        octree.py
        pathfinding.py
        position.py
        species.py
        texture_data.py
        __init__.py
        ai/
            evaluator.py
            evaluators.py
            goal.py
            __init__.py
        components/
            brain_component.py
            diet_component.py
            eat_target_component.py
            energy_component.py
            growth_component.py
            health_component.py
            memory_component.py
            move_to_target_component.py
            nutrient_source.py
            physical_body.py
            sight_sensor.py
            smell_source.py
            textured_component.py
            timer_component.py
            __init__.py
        systems/
            behaviours.py
            debug.py
            evaluations.py
            growth.py
            memory.py
            needs.py
            physics.py
            remove_components.py
            rendering.py
            senses.py
            timer.py
            __init__.py
        world/
            map.py
            terrain.py
            tile.py
            tile_column.py
            __init__.py
```

## main.py

```python
import pygame, pygame_gui, random, io, pstats, cProfile
from pygame_gui import UIManager
from pygame_gui.elements import UILabel, UIPanel, UIHorizontalSlider, UIButton
from src.world.terrain import Terrain
from src.position import Point2D, Point3D
from src.ecs import ECSCoordinator
from src.systems.rendering import renderCircles, renderTextures, renderTerrainTextures, renderSight, renderEmoticons
from src.systems.senses import senseSight
from src.systems.memory import workingMemory, assosciativeMemory
from src.systems.needs import updateNutrients, updateEnergy, damagedComponent
from src.systems.evaluations import updateEvaluations
from src.systems.behaviours import moveToTarget, eatTarget, brainValidate, epoch, emoteReset
from src.systems.growth import growth
from src.systems.remove_components import updateRemoveComponent, updateRemoveEntity, updateAddComponent, updateSizeEntity
from src.systems.timer import timerUpdate
from src import constants
from src.texture_data import TextureData

MOVEMENT_AMOUNT: int = 1

def main():
    camera: Point3D = Point3D(0, 0, 0)
    viewport: Point2D = Point2D(800, 600)
    coordinator: ECSCoordinator = ECSCoordinator()

    constants.POSITION_COMPONENT = coordinator.registerComponent()
    constants.PHYSICAL_BODY_COMPONENT = coordinator.registerComponent()
    constants.SMELL_COMPONENT = coordinator.registerComponent()
    constants.TEXTURED_COMPONENT = coordinator.registerComponent()
    constants.SPECIES_COMPONENT = coordinator.registerComponent()
    constants.BRAIN_COMPONENT = coordinator.registerComponent()
    constants.SIGHT_COMPONENT = coordinator.registerComponent()
    constants.WORKING_MEMORY_COMPONENT = coordinator.registerComponent()
    constants.ASSOSCIATIVE_MEMORY_COMPONENT = coordinator.registerComponent()
    constants.DIET_COMPONENT = coordinator.registerComponent()
    constants.HEALTH_COMPONENT = coordinator.registerComponent()
    constants.MOVE_TO_TARGET_COMPONENT = coordinator.registerComponent()
    constants.GROWTH_COMPONENT = coordinator.registerComponent()
    constants.NUTRIENT_SOURCE_COMPONENT = coordinator.registerComponent()
    constants.EAT_TARGET_COMPONENT = coordinator.registerComponent()
    constants.SIZE_HEALTH_COMPONENT = coordinator.registerComponent()
    constants.REMOVE_HEALTH_COMPONENT = coordinator.registerComponent()
    constants.REMOVE_ENTITY_COMPONENT = coordinator.registerComponent()
    constants.DIRTY_POSITION_COMPONENT = coordinator.registerComponent()
    constants.ADD_HEALTH_COMPONENT = coordinator.registerComponent()
    constants.PHYSICAL_BUZZ_COMPONENT = coordinator.registerComponent()
    constants.ENERGY_COMPONENT = coordinator.registerComponent()
    constants.DAMAGED_COMPONENT = coordinator.registerComponent()
    constants.TIMER_COMPONENT = coordinator.registerComponent()

    terrain: Terrain = Terrain(Point2D(0, 0))
    terrain.spoof()

    species_amounts = [
        350,
        600,
        50
    ]
    for species_index, species_count in enumerate(species_amounts):
        for _ in range(species_count):
            terrain.addEntity(coordinator, Point3D(random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), 5), species_index)

    
    terrain.regenerateEntityQuadtree(coordinator)

    pygame.init()
    screen = pygame.display.set_mode((viewport.x, viewport.y))
    clock = pygame.time.Clock()

    constants.textures = [
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Goat.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Tyrant.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Plant.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Meat.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/RottenMeat.png"),
    ]

    constants.sleepy = TextureData.load("../../Assets/Textures/PixelArt/TopDown/Sleeping.png")
    constants.hungy = TextureData.load("../../Assets/Textures/PixelArt/TopDown/Eat.png")
    constants.thirst_trap = TextureData.load("../../Assets/Textures/PixelArt/TopDown/Drink.png")
    constants.boot_coprolite = TextureData.load("../../Assets/Textures/PixelArt/TopDown/Roaming.png")

    def swapCircles():
        constants.DRAW_CIRCLES = not constants.DRAW_CIRCLES

    def swapSprites():
        constants.DRAW_SPRITES = not constants.DRAW_SPRITES

    def swapTerrain():
        constants.DRAW_TERRAIN = not constants.DRAW_TERRAIN

    def swapPause():
        constants.RUNNING = not constants.RUNNING

    def swapSight():
        constants.DRAW_SIGHT = not constants.DRAW_SIGHT
        
    def marchStep():
        if not constants.RUNNING:
            constants.TAKE_STEP = True
            swapPause()

    manager: UIManager = UIManager((viewport.x, viewport.y))
    debug_panel = UIPanel((viewport.x - 128, 0, 128, 64), manager=manager)
    position_label = UILabel(pygame.Rect(3, 3, 116, 26), f"Camera: {camera.x}, {camera.y}", manager, debug_panel.get_container())
    fps_label = UILabel(pygame.Rect(3, 29, 116, 26), f"FPS: {clock.get_fps():.2f}", manager, debug_panel.get_container())
    panel = UIPanel((0, 0, 128, 456), manager=manager)
    debug_circles = UIButton(pygame.Rect(3, 3, 116, 26), "Debug Circles", manager, panel.get_container(), command=swapCircles)
    debug_sprites = UIButton(pygame.Rect(3, 29, 116, 26), "Debug Sprites", manager, panel.get_container(), command=swapSprites)
    debug_terrain = UIButton(pygame.Rect(3, 55, 116, 26), "Debug Terrain", manager, panel.get_container(), command=swapTerrain)
    debug_sight = UIButton(pygame.Rect(3, 81, 116, 26), "Debug Sight", manager, panel.get_container(), command=swapSight)
    pause = UIButton(pygame.Rect(3, 107, 116, 26), "Pause", manager, panel.get_container(), command=swapPause)
    one_step = UIButton(pygame.Rect(3, 133, 116, 26), "One Step", manager, panel.get_container(), command=marchStep)
    fps_slider_label = UILabel(pygame.Rect(3, 159, 116, 26), f"FPS Cap: {constants.FPS}", manager, panel.get_container())
    fps_slider = UIHorizontalSlider(pygame.Rect(3, 182, 116, 26), constants.FPS, (1, 600), manager, panel.get_container())
    zoom_slider = UIHorizontalSlider(pygame.Rect(3, 208, 116, 26), constants.PIXELS_PER_METER, (1, 32), manager, panel.get_container())

    running: bool = True

    stutter_double: bool = True
    stutter_triple: int = 0
    stutter_thirty: int = 0

    while running:
        if stutter_thirty == 0:
            pr = cProfile.Profile()
            pr.enable()

        time_delta: float = clock.tick(constants.FPS)/1000.0
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LEFT:
                            camera.x -= MOVEMENT_AMOUNT
                            position_label.set_text(f"Camera: {camera.x}, {camera.y}")
                        case pygame.K_RIGHT:
                            camera.x += MOVEMENT_AMOUNT
                            position_label.set_text(f"Camera: {camera.x}, {camera.y}")
                        case pygame.K_DOWN:
                            camera.y += MOVEMENT_AMOUNT
                            position_label.set_text(f"Camera: {camera.x}, {camera.y}")
                        case pygame.K_UP:
                            camera.y -= MOVEMENT_AMOUNT
                            position_label.set_text(f"Camera: {camera.x}, {camera.y}")
                #case pygame_gui.UI_BUTTON_PRESSED:
                #    if event.ui_element == True:
                #        print("back")
                case pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == fps_slider:
                        constants.FPS = fps_slider.get_current_value()
                        fps_slider_label.set_text(f"FPS Cap: {constants.FPS}")
                    elif event.ui_element == zoom_slider:
                        constants.PIXELS_PER_METER = zoom_slider.get_current_value()
                        constants.PIXELS_PER_TILE = constants.PIXELS_PER_METER * constants.METERS_PER_TILE
            
            manager.process_events(event)
        
        if constants.RUNNING:
            if stutter_double:
                # MISC
                timerUpdate(coordinator)
                updateNutrients(coordinator)
                updateEnergy(coordinator)
                growth(coordinator)
            
            match stutter_thirty:
                case 0:
                    # Senses
                    senseSight(coordinator, terrain)
                case 10:
                    epoch(coordinator, terrain)
                    damagedComponent(coordinator)
                    # Memory
                    workingMemory(coordinator)
                    assosciativeMemory(coordinator)
                case 20:
                    # Evaluators
                    updateEvaluations(coordinator, terrain)
                case 25:
                    emoteReset(coordinator)
            
            if stutter_triple == 0:
                # Behaviours
                moveToTarget(coordinator, terrain)
                eatTarget(coordinator)
            
            updateAddComponent(coordinator)
            updateSizeEntity(coordinator)
            terrain.updateDirtyEntityQuadtree(coordinator)
            updateRemoveComponent(coordinator)
            updateRemoveEntity(coordinator)
            brainValidate(coordinator)
            
            stutter_double = not stutter_double
            stutter_triple += 1
            stutter_thirty += 1

            if stutter_triple == 3:
                stutter_triple = 0
            if stutter_thirty == 30:
                stutter_thirty = 0

            if stutter_double:
                fps_label.set_text(f"FPS: {clock.get_fps():.2f}")
        
        if constants.TAKE_STEP:
            constants.TAKE_STEP = False
            swapPause()
        
        manager.update(time_delta)

        # Rendering
        screen.fill((32, 48, 64))
        if constants.DRAW_TERRAIN or constants.DRAW_CIRCLES or constants.DRAW_SIGHT or constants.DRAW_SPRITES:
            entities = {tup for tup in terrain.entities.query((camera.scaleBy(1, 1, 0) - terrain.position), (camera.scaleBy(1, 1, 0) + Point3D(viewport.x // constants.PIXELS_PER_METER, viewport.y // constants.PIXELS_PER_METER, terrain.TERRAIN_SIZE * constants.METERS_PER_TILE) - terrain.position)) if tup[1] in coordinator.entities}
            if constants.DRAW_TERRAIN:
                renderTerrainTextures(coordinator, screen, camera, viewport, terrain)
            if constants.DRAW_CIRCLES:
                renderCircles(coordinator, screen, camera, viewport, terrain, entities)
            if constants.DRAW_SIGHT:
                renderSight(coordinator, screen, camera, viewport, terrain, entities)
            if constants.DRAW_SPRITES:
                renderTextures(coordinator, screen, camera, viewport, terrain, entities)
                if stutter_thirty < 25:
                    renderEmoticons(coordinator, screen, camera, viewport, terrain, entities)

        manager.draw_ui(screen)

        pygame.display.flip()

        if stutter_thirty == 0:
            pr.disable()
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
            ps.print_stats("\.py\:")
            print(s.getvalue())        

if __name__ == "__main__":
    main()
```

## __init__.py

```python

```

## src\constants.py

```python
from .world.tile import TileType, PhysicalState
from .species import Species
from .ecs import component
from .ai.evaluator import EvaluatorInstance
from .ai.evaluators import sizeThreatEvaluator, foodEvaluator, componentEvaluator
from .components.diet_component import NutrientType, NutrientStat
from .texture_data import TextureData
from .components.nutrient_source import NutrientSource
from .components.textured_component import TexturedComponent
from .components.timer_component import TimerComponent

textures: list[TextureData] = []

hungy: TextureData
sleepy: TextureData
thirst_trap: TextureData
boot_coprolite: TextureData

tile_types: list[TileType] = [
    TileType("Dirt", (236, 184, 138), TextureData.load("../../Assets/Textures/PixelArt/TopDown/Dirt.png"), PhysicalState.SOLID, [
    ]),
    TileType("Water", (36, 150, 210), TextureData.load("../../Assets/Textures/PixelArt/TopDown/Water.png"), PhysicalState.LIQUID, [
        ("nutrient_source", NutrientSource({NutrientType.WATER: 1000})),
    ]),
    TileType("Air", (255, 255, 255), None, PhysicalState.GAS)
]

species_types: list[Species] = [
    Species("Test", (0, 255, 255), 0, 1, 10, 500, 1, 10, 0.25, 0, 0, {NutrientType.PROTEIN: 200.5}, [
        NutrientStat(NutrientType.FIBER, 0.1, 3.0, 0.0025, 0.25),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.0001, 30.0)
    ], 10, 0.1, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
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
    ], 1200, 1200),
    Species("Shrub", (0, 255, 0), 2, 2, 2, 600, 0, 0, 0, 0.1, 0.001, {NutrientType.FIBER: 25.5}, [], -1, 0, True, [
        "health",
        "size_health",
        "growth",
        "remove_health"
    ], [], [
        ("remove_entity", True)
    ], 0, 0),
    Species("Carn", (155, 0, 0), 1, 3.5, 10, 500, 1, 10, 0.8, 0, 0, {NutrientType.PROTEIN: 2.5}, [
        NutrientStat(NutrientType.PROTEIN, 0.1, 300.0, 0.005, 0.15),
        NutrientStat(NutrientType.WATER, 0.01, 30.0, 0.001, 0.15)
    ], 10, 0.1, False, [
        "brain",
        "sight",
        "diet",
        "health",
        "eat_target",
        "move_to_target",
        "remove_health",
        "energy"
    ], [
        EvaluatorInstance(2, {
            "threat": [
                "eat_target"
            ]
        }),
        EvaluatorInstance(0, {}),
        EvaluatorInstance(1, {})
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
    ], 6000, 6000),
]

evaluator_types: list = [
    sizeThreatEvaluator,
    foodEvaluator,
    componentEvaluator
]

METERS_PER_TILE: int = 2
PIXELS_PER_METER: int = 8
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
REMOVE_HEALTH_COMPONENT: component
REMOVE_ENTITY_COMPONENT: component
DIRTY_POSITION_COMPONENT: component
ADD_HEALTH_COMPONENT: component
PHYSICAL_BUZZ_COMPONENT: component
ENERGY_COMPONENT: component
DAMAGED_COMPONENT: component
TIMER_COMPONENT: component

DRAW_CIRCLES: bool = False
DRAW_SPRITES: bool = True
DRAW_TERRAIN: bool = True
DRAW_SIGHT: bool = False
RUNNING: bool = True
TAKE_STEP: bool = False

FPS: int = 60
```

## src\ecs.py

```python
from typing import TypeAlias, Any
from ctypes import c_uint64

entity: TypeAlias = int
component: TypeAlias = int

class ECSCoordinator:
    def __init__(self):
        self.entities: dict[entity, set[component]] = {}
        self.__components: dict[component, dict[entity, Any]] = {}
        self.__next_entity_id: int = 0
        self.__next_component_id: int = 0
    
    def createEntity(self) -> entity:
        entity_id: entity = entity(self.__next_entity_id)
        self.entities[entity_id] = set()
        while entity(self.__next_entity_id) in self.entities:
            self.__next_entity_id += 1
        return entity_id
    
    def removeEntity(self, entity_id: entity):
        components: set[component] = self.entities.pop(entity_id)
        for component_id in components:
            self.__components[component_id].pop(entity_id)
        if entity_id < self.__next_entity_id:
            self.__next_entity_id = entity_id

    def registerComponent(self) -> component:
        component_id: component = component(self.__next_component_id)
        self.__components[component_id] = {}
        while component(self.__next_component_id) in self.__components:
            self.__next_component_id += 1
        return component_id
    
    def setComponent[T](self, entity_id: entity, component_id: component, data: T):
        self.__components[component_id][entity_id] = data
        self.entities[entity_id] |= {component_id}

    def removeComponents(self, entity_id: entity, components: set[component]):
        self.entities[entity_id] -= components
        for component in components:
            #print(component)
            self.__components[component].pop(entity_id)

    def hasComponent(self, entity_id: entity, component_id: component) -> bool:
        return component_id in self.entities[entity_id]

    def getComponent[T](self, entity_id: entity, component_id: component) -> T:
        return self.__components[component_id][entity_id]

    def getEntitiesWithComponent(self, component_id: component) -> set[entity]:
        return set(self.__components[component_id].keys())

```

## src\material.py

```python
from enum import Enum

class PhysicalState(Enum):
    SOLID = 1
    LIQUID = 2
    GAS = 3
```

## src\octree.py

```python
from .position import Point3D

class OctreeNode[T]:
    MAX_OCCUPANTS: int = 32
    MAX_DEPTH: int = 8
    MAPPED: list[Point3D] = [
        Point3D(-1, -1, -1),
        Point3D( 1, -1, -1),
        Point3D(-1,  1, -1),
        Point3D( 1,  1, -1),
        Point3D(-1, -1,  1),
        Point3D( 1, -1,  1),
        Point3D(-1,  1,  1),
        Point3D( 1,  1,  1),
    ]

    def __init__(self, position: Point3D, half_size: int, depth: int = 0):
        self.children: list[OctreeNode|None] = [None for _ in range(8)]
        self.occupants: dict[Point3D, T] = {}
        self.position = position
        self.half_size = half_size
        self.depth = depth
    
    def query(self, lower_point: Point3D, higher_point: Point3D) -> set[tuple[Point3D, T]]:
        if (self.position.x - self.half_size > higher_point.x or
            self.position.x + self.half_size < lower_point.x or
            self.position.y - self.half_size > higher_point.y or
            self.position.y + self.half_size < lower_point.y or
            self.position.z - self.half_size > higher_point.z or
            self.position.z + self.half_size < lower_point.z):
            return set()
        elif self.children[0] == None:
            return {(pos, child) for pos, child in self.occupants.items() if (lower_point.x <= pos.x <= higher_point.x and
                                                          lower_point.y <= pos.y <= higher_point.y and
                                                          lower_point.z <= pos.z <= higher_point.z)}
        else:
            to_return = set()
            for child in self.children:
                to_return |= child.query(lower_point, higher_point)
            return to_return
    
    def insert(self, position: Point3D, data: T):
        if not (self.position.x - self.half_size <= position.x <= self.position.x + self.half_size and
                self.position.y - self.half_size <= position.y <= self.position.y + self.half_size and
                self.position.z - self.half_size <= position.z <= self.position.z + self.half_size):
            return
        elif self.children[0] == None:
            self.occupants[position] = data
            if len(self.occupants) == OctreeNode.MAX_OCCUPANTS and self.depth < OctreeNode.MAX_DEPTH:
                new_half = self.half_size // 2
                for i in range(8):
                    node_position: Point3D = Point3D(self.position.x, self.position.y, self.position.z) + OctreeNode.MAPPED[i] * new_half
                    self.children[i] = OctreeNode[T](node_position, new_half, self.depth + 1)
                for position2, occupant in self.occupants.items():
                    x = int(position2.x > self.position.x)
                    y = int(position2.y > self.position.y)
                    z = int(position2.z > self.position.z)
                    self.children[x + y * 2 + z * 4].insert(position2, occupant)
                self.occupants = {}
                return
        else:
            x = int(position.x > self.position.x)
            y = int(position.y > self.position.y)
            z = int(position.z > self.position.z)
            self.children[x + y * 2 + z * 4].insert(position, data)
    
    def pop(self, position: Point3D) -> bool:
        if not (self.position.x - self.half_size <= position.x <= self.position.x + self.half_size and
                self.position.y - self.half_size <= position.y <= self.position.y + self.half_size and
                self.position.z - self.half_size <= position.z <= self.position.z + self.half_size):
            return False
        elif self.children[0] == None:
            return self.occupants.pop(position, None) != None
        else:
            for child in self.children:
                if child.pop(position):
                    return True
            return False
```

## src\pathfinding.py

```python

```

## src\position.py

```python
from dataclasses import dataclass
from numbers import Complex

@dataclass(unsafe_hash=True)
class Point2D:
    x: float
    y: float

    @classmethod
    def fromUniform(cls, value: float):
        return Point2D(value, value)
    
    def asPoint3D(self):
        return Point3D(self.x, self.y, 0)
    
    def __add__(self, other):
        return Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point2D(self.x - other.x, self.y - other.y)
    
    def scaleBy(self, x: float, y: float):
        return Point2D(self.x * x, self.y * y)
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x * other, self.y * other)
        
    def __floordiv__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x / other, self.y / other)
        
    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Point2D(self.x / other, self.y / other)
        
    def dist(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def distSQ(self, other) -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2
    
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def norm(self) -> "Point2D":
        return self / self.magnitude()

@dataclass(unsafe_hash=True)
class Point3D:
    x: float
    y: float
    z: float

    @classmethod
    def fromUniform(cls, value: float):
        return Point3D(value, value, value)

    def asPoint2D(self):
        return Point2D(self.x, self.y)
    
    def __add__(self, other):
        if isinstance(other, Point3D):
            return Point3D(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, Point2D):
            return Point3D(self.x + other.x, self.y + other.y, self.z)

    def __sub__(self, other):
        if isinstance(other, Point3D):
            return Point3D(self.x - other.x, self.y - other.y, self.z - other.z)
        elif isinstance(other, Point2D):
            return Point3D(self.x - other.x, self.y - other.y, self.z)
    
    def scaleBy(self, x: float, y: float, z: float):
        return Point3D(self.x * x, self.y * y, self.z * z)
    
    def __mul__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x * other, self.y * other, self.z * other)
    
    def __floordiv__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x / other, self.y / other, self.z / other)
    
    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Point3D(self.x / other, self.y / other, self.z / other)
        
    def dist(self, other) -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2) ** 0.5
    
    def distSQ(self, other) -> float:
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
    
    def magnitude(self) -> float:
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def norm(self) -> "Point3D":
        return self / self.magnitude()
```

## src\species.py

```python
from .ai.evaluator import EvaluatorInstance
from .components.diet_component import NutrientType, NutrientStat
from typing import Any

class Species:
    def __init__(self, name: str, color, texture: int, size: float, mass: float, max_life: int, speed: float, sight: float, sight_factor: float, growth_max_amount: float, growth_amount: float, nutrients: dict[NutrientType, float], diet: list[NutrientStat], eats: int, eat_amount: float, size_health: bool, remover: list[str], evaluators: list[EvaluatorInstance], adder: list[tuple[str, Any]], energy_max: int, energy: int):
        self.name = name
        self.color = color
        self.texture = texture
        self.size = size
        self.mass = mass
        self.max_life = max_life
        self.speed = speed
        self.sight = sight
        self.sight_factor = sight_factor
        self.growth_max_amount = growth_max_amount
        self.growth_amount = growth_amount
        self.nutrients = nutrients
        self.diet = diet
        self.eats = eats
        self.eat_amount = eat_amount
        self.size_health = size_health
        self.remover = remover
        self.evaluators = evaluators
        self.adder = adder
        self.energy_max = energy_max
        self.energy = energy
```

## src\texture_data.py

```python
from dataclasses import dataclass
import pygame
from pygame import Surface, Rect

@dataclass
class TextureData:
    texture: Surface
    rect: Rect

    @classmethod
    def load(cls, filepath):
        surface: Surface = pygame.image.load(filepath)
        rect: Rect = surface.get_rect()
        return cls(surface, rect)
```

## src\__init__.py

```python

```

## src\ai\evaluator.py

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class EvaluatorInstance:
    def __init__(self, evaluator_id: int, data: dict[str, Any]):
        self.evaluator_id = evaluator_id
        self.data = data
```

## src\ai\evaluators.py

```python
from .evaluator import Any
from ..ecs import ECSCoordinator, entity, component
from ..components.brain_component import BrainComponent
from ..components.diet_component import DietComponent
from ..components.nutrient_source import NutrientSource
from ..components.physical_body import PhysicalBody
#from ..world.terrain import Terrain
from .. import constants
import math

#def targetEvaluator(coordinator: ECSCoordinator, entity_id: entity, terrain: "Terrain", data: dict[str, Any]):
#    brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
#    if len(brain.entities) > 0:
#        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
#        closest_point = sorted(brain.entities, key = lambda tup: position.distSQ(tup[0]))[0][0]
#        brain.target_position.setPosition(closest_point, PositionContext.ROAM)

def foodEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, terrain: "Terrain", data: dict[str, Any]):
    diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
    amount: float = 0.0
    if coordinator.hasComponent(entity_id, constants.EAT_TARGET_COMPONENT):
        amount = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT).amount

    listable = diet.orderedStats(amount)
    for i, entity_instance in enumerate(brain.entities):
        if coordinator.hasComponent(entity_instance.id, constants.NUTRIENT_SOURCE_COMPONENT):
            nutrient_source: NutrientSource = coordinator.getComponent(entity_instance.id, constants.NUTRIENT_SOURCE_COMPONENT)
            physical_body: PhysicalBody = coordinator.getComponent(entity_instance.id, constants.PHYSICAL_BODY_COMPONENT)
            nutrient_value = 0.0
            for nutrient_type, nutrient_need, nutrient_consumption in listable:
                nutrient_value += nutrient_need * nutrient_consumption * nutrient_source.nutrients.get(nutrient_type, 0) * ((physical_body.size * 0.5) ** 2) * math.pi
            brain.entities[i].nutrition = nutrient_value

def sizeThreatEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, terrain: "Terrain", data: dict[str, Any]):
    physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
    for i, entity_instance in enumerate(brain.entities):
        if brain.entities[i].threat != None:
            brain.entities[i].threat += (coordinator.getComponent(entity_instance.id, constants.PHYSICAL_BODY_COMPONENT).size - physical_body.size) * data.get("modifier", 1.0)

def componentEvaluator(coordinator: ECSCoordinator, entity_id: entity, brain: BrainComponent, terrain: "Terrain", data: dict[str, Any]):
    components: list[component] = map(constants.componentPull, data["threat"])
    for i, entity_eval in enumerate(brain.entities):
        for component_type in components:
            if coordinator.hasComponent(entity_eval.id, component_type):
                brain.entities[i].threat = 0.0
                break

```

## src\ai\goal.py

```python

```

## src\ai\__init__.py

```python

```

## src\components\brain_component.py

```python
from dataclasses import dataclass
from enum import Enum
from ..position import Point3D
from ..ecs import entity
from ..ai.evaluator import EvaluatorInstance

class PositionContext(Enum):
    SAFETY = 0
    FOOD = 1
    FIGHT = 2
    ROAM = 3
    MATE = 4

@dataclass
class EntityTarget:
    position: Point3D
    id: entity
    threat: float = None
    nutrition: float = None

    def threatByDistance(self, point: Point3D):
        return (self.threat * abs(self.threat)) / (point.distSQ(self.position) if self.position != point else 1.0) if self.threat != None else 0.0

    def nutritionByDistance(self, point: Point3D):
        return self.nutrition / (point.distSQ(self.position) if self.position != point else 1.0) if self.nutrition != None else 0.0

@dataclass
class TargetPosition:
    position: Point3D
    context: PositionContext
    valid: bool = False

    def setPosition(self, position: Point3D, context: PositionContext):
        self.position = position
        self.context = context
        self.valid = True
    
    def invalidate(self):
        self.valid = False

@dataclass
class TargetCreature:
    creature: entity
    valid: bool = False

    def setCreature(self, creature: entity):
        self.creature = creature
        self.valid = True

class CreatureState(Enum):
    AWAKE = 0
    SLEEPING = 1

class Emoticon(Enum):
    NONE = 0
    EATING = 1
    DRINKING = 2
    ROAMING = 3

@dataclass
class BrainComponent:
    evaluators: list[EvaluatorInstance]
    entities: list[EntityTarget]
    target_position: TargetPosition
    target_creature: TargetCreature
    state: CreatureState = CreatureState.AWAKE
    emoticon: Emoticon = Emoticon.NONE

```

## src\components\diet_component.py

```python
from dataclasses import dataclass
from enum import Enum

class NutrientType(Enum):
    PROTEIN = 0
    WATER = 1
    ELECTROLYTE = 2
    FIBER = 3
    VITAMIN = 4    

@dataclass
class NutrientStat:
    nutrient: NutrientType
    minimum: float
    maximum: float
    consume: float
    current: float

@dataclass
class DietComponent:
    nutrients: list[NutrientStat]

    def orderedStats(self, amount: float) -> list[tuple[NutrientType, float, float]]:
        return sorted([(nutrient_stat.nutrient, ((nutrient_stat.maximum - nutrient_stat.minimum) - (nutrient_stat.current + amount - nutrient_stat.minimum)) / nutrient_stat.consume, nutrient_stat.consume) for nutrient_stat in self.nutrients], key = lambda tup: tup[1])

    def updated(self, nutrient: "NutrientSource", amount: float) -> "DietComponent":
        return DietComponent([NutrientStat(instance.nutrient, instance.minimum, instance.maximum, instance.consume, instance.current + min(nutrient.nutrients.get(instance.nutrient, 0), amount)) for instance in self.nutrients])
```

## src\components\eat_target_component.py

```python
from dataclasses import dataclass

@dataclass
class EatTargetComponent:
    damage: int
    amount: float
```

## src\components\energy_component.py

```python
from dataclasses import dataclass

@dataclass
class EnergyComponent:
    current: int
    max: int
```

## src\components\growth_component.py

```python
from dataclasses import dataclass

@dataclass
class GrowthComponent:
    amount: float
    max_amount: float
    current: float = 0
```

## src\components\health_component.py

```python
from dataclasses import dataclass

@dataclass
class HealthComponent:
    current: int
    max: int
```

## src\components\memory_component.py

```python
from dataclasses import dataclass
from typing import Any
from enum import Enum

class MemoryType(Enum):
    ACTIVE_TARGET = 0
    ACTIVE_ALLY = 1
    MATE = 2
    CLOSE_RELATION = 3
    CORPSE = 4
    PAST_THREAT = 5

@dataclass
class MemorySlot:
    memory_type: MemoryType
    memory_data: Any
    memory_decay: int

@dataclass
class MemoryComponent:
    slots: set[MemorySlot]
```

## src\components\move_to_target_component.py

```python
from dataclasses import dataclass

@dataclass
class MoveToTargetComponent:
    speed: float
```

## src\components\nutrient_source.py

```python
from dataclasses import dataclass
from .diet_component import NutrientType

@dataclass
class NutrientSource:
    nutrients: dict[NutrientType, float]
```

## src\components\physical_body.py

```python
from dataclasses import dataclass

@dataclass
class PhysicalBody:
    mass: float
    size: float
    rotation: float = 0
    color: tuple[int, int, int] = (0, 0, 0)
```

## src\components\sight_sensor.py

```python
from dataclasses import dataclass

@dataclass
class SightSensor:
    distance: float
    offset_factor: float
```

## src\components\smell_source.py

```python
from dataclasses import dataclass

@dataclass
class SmellSource:
    smell_type: int
    smell_strength: int
```

## src\components\textured_component.py

```python
from dataclasses import dataclass

@dataclass
class TexturedComponent:
    texture_id: int
    draw_centered: bool = True
```

## src\components\timer_component.py

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class TimerComponent:
    current: int
    time: int
    remove: list[str]
    add: list[tuple[str, Any]]
```

## src\components\__init__.py

```python

```

## src\systems\behaviours.py

```python
from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point3D, Point3D
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.eat_target_component import EatTargetComponent
from ..components.brain_component import BrainComponent, Emoticon
from ..components.physical_body import PhysicalBody
from ..components.diet_component import DietComponent
from ..components.nutrient_source import NutrientSource
from ..components.health_component import HealthComponent
from .. import constants
import math, random

def moveToTarget(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.MOVE_TO_TARGET_COMPONENT):
        move_to_target: MoveToTargetComponent = coordinator.getComponent(entity_id, constants.MOVE_TO_TARGET_COMPONENT)
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_position.valid:
            distance: Point3D = (brain_component.target_position.position - position)
            distance.z = 0
            physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)

            if distance.magnitude() > physical_body.size:
                direction: Point3D = distance.norm()
                angle = math.degrees(math.atan2(direction.y, direction.x))
                physical_body.rotation = 270 - angle
                coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)
                coordinator.setComponent(entity_id, constants.DIRTY_POSITION_COMPONENT, position)
                coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + (direction * move_to_target.speed))
                
                energy = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
                energy.current -= max(math.floor(move_to_target.speed), 1)
                coordinator.setComponent(entity_id, constants.ENERGY_COMPONENT, energy)

def eatTarget(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.EAT_TARGET_COMPONENT):
        eat_target: EatTargetComponent = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT)
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_creature.valid and brain_component.target_creature.creature in coordinator.entities:
            entity_pos: Point3D = coordinator.getComponent(brain_component.target_creature.creature, constants.POSITION_COMPONENT)
            entity_size: Point3D = coordinator.getComponent(brain_component.target_creature.creature, constants.PHYSICAL_BODY_COMPONENT).size
            size_modification = entity_size
            if coordinator.hasComponent(brain_component.target_creature.creature, constants.SIZE_HEALTH_COMPONENT):
                health = coordinator.getComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT)
                size_modification *= health.current / health.max
            if entity_pos.distSQ(position) <= (size_modification + physical_body.size) ** 2:
                distance_to_target = entity_pos - position
                if distance_to_target.magnitude() != 0:
                    direction: Point3D = distance_to_target.norm()
                    angle = math.degrees(math.atan2(direction.y, direction.x))
                    physical_body.rotation = 270 - angle
                    coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)
                diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
                nutrition: NutrientSource = coordinator.getComponent(brain_component.target_creature.creature, constants.NUTRIENT_SOURCE_COMPONENT)
                if constants.NutrientType.WATER in nutrition.nutrients and len(nutrition.nutrients) == 1:
                    brain_component.emoticon = Emoticon.DRINKING
                else:
                    brain_component.emoticon = Emoticon.EATING
                coordinator.setComponent(entity_id, constants.DIET_COMPONENT, diet.updated(nutrition, eat_target.amount))
                if coordinator.hasComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT):
                    health: HealthComponent = coordinator.getComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT)
                    health.current = min(max(health.current - eat_target.damage, 0), health.max)
                    coordinator.setComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT, health)
                    coordinator.setComponent(brain_component.target_creature.creature, constants.DAMAGED_COMPONENT, (255, 0, 0))
                elif coordinator.hasComponent(brain_component.target_creature.creature, constants.PHYSICAL_BUZZ_COMPONENT):
                    target_physical_body: PhysicalBody = coordinator.getComponent(brain_component.target_creature.creature, constants.PHYSICAL_BODY_COMPONENT)
                    target_physical_body.size -= eat_target.damage / 360
                energy = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
                energy.current -= eat_target.damage
                coordinator.setComponent(entity_id, constants.ENERGY_COMPONENT, energy)


def brainValidate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        brain_component.entities = [entity_instance for entity_instance in brain_component.entities if entity_instance.id not in coordinator.entities]

def epoch(coordinator: ECSCoordinator, terrain: Terrain):
    filled_positions = set()
    for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        while position in filled_positions:
            position += Point3D(random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01))
        coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position)
        filled_positions.add(position)

def emoteReset(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        brain_component.emoticon = Emoticon.NONE
```

## src\systems\debug.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..position import Point3D
import random

def randomMovement(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + Point3D(random.randint(-1, 1), random.randint(-1, 1), 0))
```

## src\systems\evaluations.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.brain_component import BrainComponent, PositionContext, CreatureState
from ..components.energy_component import EnergyComponent
from ..world.terrain import Terrain
from ..position import Point3D

from random import randint

def updateEvaluations(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        energon: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)

        sleepy = (energon.max - energon.current) / energon.max
        if brain_component.state == CreatureState.AWAKE:
            pos = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            for evaluator in brain_component.evaluators:
                constants.evaluator_types[evaluator.evaluator_id](coordinator, entity_id, brain_component, terrain, evaluator.data)

            if sleepy > 0.9:
                brain_component.state = CreatureState.SLEEPING
                brain_component.target_creature.valid = False
                brain_component.target_position.valid = False
            elif len(brain_component.entities) > 0:
                sortation = sorted(brain_component.entities, key=lambda x: x.nutritionByDistance(pos) - x.threatByDistance(pos), reverse=True)[0]
                if sortation.nutrition > 0:
                    brain_component.target_creature.setCreature(sortation.id)
                    brain_component.target_position.setPosition(coordinator.getComponent(sortation.id, constants.POSITION_COMPONENT), PositionContext.FOOD)
                else:
                    brain_component.target_creature.valid = False
                    brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
            else:
                brain_component.target_creature.valid = False
                brain_component.target_position.setPosition(pos + Point3D(randint(-12, 12), randint(-12, 12), 5), PositionContext.ROAM)
        elif brain_component.state == CreatureState.SLEEPING:
            if sleepy < 0.1:
                brain_component.state = CreatureState.AWAKE

```

## src\systems\growth.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.growth_component import GrowthComponent
from ..components.physical_body import PhysicalBody

def growth(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.GROWTH_COMPONENT):
        growth_component: GrowthComponent = coordinator.getComponent(entity_id, constants.GROWTH_COMPONENT)
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        if growth_component.max_amount > growth_component.current:
            growth_component.current += growth_component.amount
            physical_body.size += growth_component.amount
            coordinator.setComponent(entity_id, constants.GROWTH_COMPONENT, growth_component)
            coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)
```

## src\systems\memory.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.memory_component import MemoryComponent

def workingMemory(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.WORKING_MEMORY_COMPONENT):
        working_memory: MemoryComponent = coordinator.getComponent(entity_id, constants.WORKING_MEMORY_COMPONENT)

def assosciativeMemory(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ASSOSCIATIVE_MEMORY_COMPONENT):
        assosciative_memory: MemoryComponent = coordinator.getComponent(entity_id, constants.ASSOSCIATIVE_MEMORY_COMPONENT)
        
```

## src\systems\needs.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.diet_component import DietComponent
from ..components.health_component import HealthComponent
from ..components.energy_component import EnergyComponent
from ..components.brain_component import BrainComponent, CreatureState

def updateNutrients(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.DIET_COMPONENT):
        diet_component: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        for nutrient in diet_component.nutrients:
            nutrient.current = max(nutrient.current - nutrient.consume, 0)
            if nutrient.minimum <= nutrient.current <= nutrient.maximum:
                health_component.current = min(health_component.current + 1, health_component.max)
            else:
                health_component.current -= 1
                
def updateEnergy(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ENERGY_COMPONENT):
        energy_component: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        match brain_component.state:
            case CreatureState.SLEEPING:
                energy_component.current += 10
            case CreatureState.AWAKE:
                energy_component.current -= 1

def damagedComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.DAMAGED_COMPONENT):
        coordinator.removeComponents(entity_id, {constants.DAMAGED_COMPONENT})

```

## src\systems\physics.py

```python
from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from ..components.sight_sensor import SightSensor
from ..components.brain_component import BrainComponent
from .. import constants

def physics(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.SIGHT_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
```

## src\systems\remove_components.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.health_component import HealthComponent
from ..components.physical_body import PhysicalBody
from ..components.timer_component import TimerComponent

def updateRemoveComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_HEALTH_COMPONENT):
        remove_component: list[str] = coordinator.getComponent(entity_id, constants.REMOVE_HEALTH_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            coordinator.removeComponents(entity_id, set(map(constants.componentPull, remove_component)))
                
def updateAddComponent(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.ADD_HEALTH_COMPONENT):
        add_component: list[tuple[str, ...]] = coordinator.getComponent(entity_id, constants.ADD_HEALTH_COMPONENT)
        health_component: HealthComponent = coordinator.getComponent(entity_id, constants.HEALTH_COMPONENT)
        if health_component.current == 0:
            for component_type, component_data in add_component:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), component_data if component_type != "timer" else TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()))
            coordinator.removeComponents(entity_id, {constants.ADD_HEALTH_COMPONENT})

def updateRemoveEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REMOVE_ENTITY_COMPONENT):
        coordinator.removeEntity(entity_id)

def updateSizeEntity(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.PHYSICAL_BUZZ_COMPONENT):
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        if physical_body.size <= 0:
            physical_buzz = coordinator.getComponent(entity_id, constants.PHYSICAL_BUZZ_COMPONENT)
            for component_type, component_data in physical_buzz[1]:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), component_data if component_type != "timer" else TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.PHYSICAL_BUZZ_COMPONENT}) | set(map(constants.componentPull, physical_buzz[0])))
```

## src\systems\rendering.py

```python
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
            scaled_terrain_texture = pygame.transform.scale_by(texture.texture, scaling_factor)
            scaled_terrain_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)

            surface.blit(scaled_terrain_texture, scaled_terrain_rect)

def renderCircles(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
    for position, entity in entities:
        physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        scaling_factor = physical_body.size
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        filled_circle(surface, int(new_position.x), int(new_position.y), int(scaling_factor * constants.PIXELS_PER_METER), physical_body.color)

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

def renderEmoticons(coordinator: ECSCoordinator, surface: Surface, camera: Point3D, view_size: Point2D, terrain: Terrain, entities: set[tuple[Point3D, entity]]):
    for position, entity in (entities):
        if not coordinator.hasComponent(entity, constants.BRAIN_COMPONENT) or not coordinator.hasComponent(entity, constants.TEXTURED_COMPONENT):
            continue
        brain: BrainComponent = coordinator.getComponent(entity, constants.BRAIN_COMPONENT)
        if brain.state == CreatureState.AWAKE and brain.emoticon == Emoticon.NONE:
            continue
        physical_body: PhysicalBody = coordinator.getComponent(entity, constants.PHYSICAL_BODY_COMPONENT)
        texture_component: TexturedComponent = coordinator.getComponent(entity, constants.TEXTURED_COMPONENT)
        texture: TextureData = constants.textures[texture_component.texture_id]
        scaling_factor: float = constants.PIXELS_PER_METER / max(texture.rect.width, texture.rect.height) * physical_body.size * 2
        if coordinator.hasComponent(entity, constants.SIZE_HEALTH_COMPONENT):
            health = coordinator.getComponent(entity, constants.HEALTH_COMPONENT)
            scaling_factor *= health.current / health.max
        new_position = (position.asPoint2D()  - camera) * constants.PIXELS_PER_METER
        scaled_entity_rect = Rect(int(new_position.x - texture.rect.width * scaling_factor * 0.5), int(new_position.y - texture.rect.height * scaling_factor * 0.5), texture.rect.width * scaling_factor, texture.rect.height * scaling_factor)
        
        if brain.state == CreatureState.SLEEPING:
            emoticon_texture_data: TextureData = constants.sleepy
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 4.0)
        elif brain.emoticon == Emoticon.EATING:
            emoticon_texture_data: TextureData = constants.hungy
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.DRINKING:
            emoticon_texture_data: TextureData = constants.thirst_trap
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        elif brain.emoticon == Emoticon.ROAMING:
            emoticon_texture_data: TextureData = constants.boot_coprolite
            emoticon_texture: Surface = pygame.transform.scale_by(emoticon_texture_data.texture, constants.PIXELS_PER_METER / max(emoticon_texture_data.rect.width, emoticon_texture_data.rect.height) * 1.5)
        
        
        emoticon_rect = emoticon_texture.get_rect()
        emoticon_rect.center =  (scaled_entity_rect.centerx, scaled_entity_rect.centery + constants.PIXELS_PER_METER / 12)

        surface.blit(emoticon_texture, emoticon_rect)
```

## src\systems\senses.py

```python
from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Point2D, Point3D
from ..components.sight_sensor import SightSensor
from ..components.brain_component import BrainComponent, EntityTarget, PositionContext, Emoticon
from ..components.physical_body import PhysicalBody
from .. import constants
import math

def senseSight(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.SIGHT_COMPONENT):
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        sight_range: SightSensor = coordinator.getComponent(entity_id, constants.SIGHT_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_position.valid and brain_component.target_position.context == PositionContext.ROAM:
            brain_component.emoticon = Emoticon.ROAMING
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        angle: float = math.radians(270 - physical_body.rotation)
        rotation_offset: Point3D = Point3D(math.cos(angle), math.sin(angle), 0) * sight_range.distance * sight_range.offset_factor
        brain_component.entities = [EntityTarget(position, entity_id_iter) for position, entity_id_iter in terrain.entities.query(position + rotation_offset - Point3D.fromUniform(sight_range.distance), position + rotation_offset + Point3D.fromUniform(sight_range.distance)) if entity_id_iter != entity_id]
```

## src\systems\timer.py

```python
from ..ecs import ECSCoordinator
from .. import constants
from ..components.timer_component import TimerComponent

def timerUpdate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.TIMER_COMPONENT):
        timer: TimerComponent = coordinator.getComponent(entity_id, constants.TIMER_COMPONENT)
        timer.current += 1
        if timer.current >= timer.time:
            for component_type, component_data in timer.add:
                coordinator.setComponent(entity_id, constants.componentPull(component_type), component_data if component_type != "timer" else TimerComponent(0, component_data.time, component_data.remove.copy(), component_data.add.copy()))
            coordinator.removeComponents(entity_id, set({constants.TIMER_COMPONENT}) | set(map(constants.componentPull, timer.remove)))
```

## src\systems\__init__.py

```python

```

## src\world\map.py

```python
class Map:
    def __init__(self):
        ...
```

## src\world\terrain.py

```python
from .tile import ColumnLayerData
from .tile_column import TileColumn
from ..octree import OctreeNode, Point3D
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
                tile_components = column.getComponents()
                if len(tile_components) > 0:
                    tile_entity = coordinator.createEntity()
                    for component_type, component_data in tile_components:
                        coordinator.setComponent(tile_entity, constants.componentPull(component_type), component_data)
                    coordinator.setComponent(tile_entity, constants.POSITION_COMPONENT, Point3D((x + 0.5) * constants.METERS_PER_TILE, (y + 0.5) * constants.METERS_PER_TILE, 2))
                    coordinator.setComponent(tile_entity, constants.PHYSICAL_BODY_COMPONENT, PhysicalBody(100, constants.METERS_PER_TILE / 2))
        
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
        return new_entity
```

## src\world\tile.py

```python
from ..material import PhysicalState
from typing import NamedTuple
from ..texture_data import TextureData

class TileType:
    def __init__(self, name: str, color, texture: TextureData, state: PhysicalState, components: list = []):
        self.name = name
        self.color = color
        self.texture = texture
        self.state = state
        self.components = components


class ColumnLayerData(NamedTuple):
    tile_type: int
    height: float
```

## src\world\tile_column.py

```python
from .tile import ColumnLayerData, PhysicalState
from .. import constants

class TileColumn:
    def __init__(self):
        self.layers: list[ColumnLayerData] = []
    
    def getComponents(self):
        to_return = []
        for layer in self.layers:
            to_return.extend(constants.tile_types[layer.tile_type].components)
        return to_return
    
    def topLayer(self) -> ColumnLayerData|None:
        for layer in reversed(self.layers):
            if constants.tile_types[layer.tile_type].state != PhysicalState.GAS:
                return layer
        return None
```

## src\world\__init__.py

```python

```

