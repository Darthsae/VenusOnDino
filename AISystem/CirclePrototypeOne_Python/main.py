import pygame, pygame_gui, random, io, pstats, cProfile
from pygame_gui import UIManager
from pygame_gui.elements import UILabel, UIPanel, UIProgressBar, UIHorizontalSlider, UIButton
from src.world.terrain import Terrain
from src.position import Point2D, Point3D
from src.ecs import ECSCoordinator
from src.systems.rendering import renderCircles, renderTextures, renderTerrain
from src.systems.debug import randomMovement
from src.systems.senses import senseSight
from src.systems.memory import workingMemory, assosciativeMemory
from src.systems.needs import updateNutrients
from src.systems.evaluations import updateEvaluations
from src.systems.behaviours import moveToTarget, eatTarget
from src.systems.growth import growth
from src.systems.remove_components import updateRemoveComponent
from src import constants
from src.texture_data import TextureData

MOVEMENT_AMOUNT: int = 1

def main():
    camera: Point3D = Point3D(0, 0, 0)
    viewport: Point2D = Point2D(960, 540)
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

    terrain: Terrain = Terrain(Point2D(0, 0))
    terrain.spoof()

    for _ in range(1000):
        terrain.addEntity(coordinator, Point3D(random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), 5), random.randint(0, len(constants.species_types) - 1))

    
    terrain.regenerateEntityQuadtree(coordinator)

    pygame.init()
    screen = pygame.display.set_mode((viewport.x, viewport.y))
    clock = pygame.time.Clock()

    constants.textures = [
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Tyrant.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Titan.png")
    ]

    def swapCircles():
        constants.DRAW_CIRCLES = not constants.DRAW_CIRCLES

    def swapSprites():
        constants.DRAW_SPRITES = not constants.DRAW_SPRITES

    def swapTerrain():
        constants.DRAW_TERRAIN = not constants.DRAW_TERRAIN

    def swapPause():
        constants.RUNNING = not constants.RUNNING
        
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
    pause = UIButton(pygame.Rect(3, 81, 116, 26), "Pause", manager, panel.get_container(), command=swapPause)
    one_step = UIButton(pygame.Rect(3, 107, 116, 26), "One Step", manager, panel.get_container(), command=marchStep)
    fps_slider_label = UILabel(pygame.Rect(3, 133, 116, 26), f"FPS Cap: {constants.FPS}", manager, panel.get_container())
    fps_slider = UIHorizontalSlider(pygame.Rect(3, 159, 116, 26), constants.FPS, (1, 600), manager, panel.get_container())

    running: bool = True

    stutter_double: bool = True
    stutter_triple: int = 0
    stutter_thirty: int = 0

    while running:
        #if stutter_thirty == 0:
        #    pr = cProfile.Profile()
        #    pr.enable()

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
            
            manager.process_events(event)
        
        if constants.RUNNING:
            if stutter_double:
                # MISC
                updateNutrients(coordinator)
                growth(coordinator)
            
            match stutter_thirty:
                case 0:
                    # Senses
                    senseSight(coordinator, terrain)
                case 10:
                    # Memory
                    workingMemory(coordinator)
                    assosciativeMemory(coordinator)
                case 20:
                    # Evaluators
                    updateEvaluations(coordinator, terrain)
            
            if stutter_triple == 0:
                # Behaviours
                moveToTarget(coordinator, terrain)
                eatTarget(coordinator)
            
            terrain.updateDirtyEntityQuadtree(coordinator)
            updateRemoveComponent(coordinator)
            
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
        if constants.DRAW_TERRAIN:
            renderTerrain(coordinator, screen, camera, viewport, terrain)
        if constants.DRAW_CIRCLES:
            renderCircles(coordinator, screen, camera, viewport, terrain)
        if constants.DRAW_SPRITES:
            renderTextures(coordinator, screen, camera, viewport, terrain)

        manager.draw_ui(screen)

        pygame.display.flip()

        #if stutter_thirty == 0:
        #    pr.disable()
        #    s = io.StringIO()
        #    ps = pstats.Stats(pr, stream=s).strip_dirs().sort_stats(pstats.SortKey.CUMULATIVE)
        #    ps.print_stats("\.py\:")
        #    print(s.getvalue())        

if __name__ == "__main__":
    main()