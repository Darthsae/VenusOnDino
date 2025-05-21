import pygame, pygame_gui, random
from pygame_gui import UIManager
from pygame_gui.elements import UILabel
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

    terrain: Terrain = Terrain(Point2D(0, 0))
    terrain.spoof()

    for _ in range(100):
        terrain.addEntity(coordinator, Point3D(random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), random.randint(0, Terrain.TERRAIN_SIZE * constants.METERS_PER_TILE), 5), random.randint(0, len(constants.species_types) - 1))

    pygame.init()
    screen = pygame.display.set_mode((viewport.x, viewport.y))

    constants.textures = [
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Tyrant.png"),
        TextureData.load("../../Assets/Textures/PixelArt/TopDown/Titan.png")
    ]
    
    manager: UIManager = UIManager((viewport.x, viewport.y))
    positionLabel = UILabel(pygame.Rect(viewport.x - 128, 0, 128, 32), f"{camera.x}, {camera.y}", manager)
    clock = pygame.time.Clock()

    running = True

    while running:
        time_delta: float = clock.tick(60)/1000.0
        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_LEFT:
                            camera.x -= MOVEMENT_AMOUNT
                        case pygame.K_RIGHT:
                            camera.x += MOVEMENT_AMOUNT
                        case pygame.K_DOWN:
                            camera.y += MOVEMENT_AMOUNT
                        case pygame.K_UP:
                            camera.y -= MOVEMENT_AMOUNT
                case pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == True:
                        print("back")
            
            manager.process_events(event)
        
        #randomMovement(coordinator)
        updateNutrients(coordinator)
        growth(coordinator)
        senseSight(coordinator, terrain)
        workingMemory(coordinator)
        assosciativeMemory(coordinator)
        updateEvaluations(coordinator, terrain)
        moveToTarget(coordinator, terrain)
        eatTarget(coordinator)

        positionLabel.set_text(f"{camera.x}, {camera.y}")
        
        manager.update(time_delta)

        terrain.regenerateEntityQuadtree(coordinator)

        renderTerrain(coordinator, screen, camera, viewport, terrain)
        renderCircles(coordinator, screen, camera, viewport, terrain)
        renderTextures(coordinator, screen, camera, viewport, terrain)

        manager.draw_ui(screen)

        pygame.display.flip()

if __name__ == "__main__":
    main()