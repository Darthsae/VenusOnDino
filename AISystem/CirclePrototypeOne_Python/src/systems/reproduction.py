from ..ecs import ECSCoordinator, entity
from ..world.terrain import Terrain
from ..position import Point3D
from ..components.energy_component import EnergyComponent
from ..components.reproduce_component import ReproduceComponent, Sex
from ..components.physical_body import PhysicalBody
from ..components.brain_component import BrainComponent, CreatureState
from .. import constants
import random

def updateReproduction(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REPRODUCE_COMPONENT):
        reproduce_component: ReproduceComponent = coordinator.getComponent(entity_id, constants.REPRODUCE_COMPONENT)
        
        if random.random() > reproduce_component.chance:
            continue

        if coordinator.hasComponent(entity_id, constants.BRAIN_COMPONENT) and coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT).state != CreatureState.AWAKE:
            continue

        if coordinator.hasComponent(entity_id, constants.ENERGY_COMPONENT):
            energy: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
            if energy.current < reproduce_component.energy_use:
                continue
            energy.current -= reproduce_component.energy_use

        mod = 1.0
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        if reproduce_component.others != 0:
            physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
            view_size: Point3D = Point3D.fromUniform(physical_body.size * 2)
            possible: set[tuple[Point3D, entity]] = terrain.entities.query(position - view_size, position + view_size)
            success: bool = reproduce_component.others != 1
            id_of_self: int = coordinator.getComponent(entity_id, constants.SPECIES_COMPONENT)
            for _, entity_id_iter in possible:
                if entity_id_iter in coordinator.entities and coordinator.hasComponent(entity_id_iter, constants.REPRODUCE_COMPONENT) and coordinator.hasComponent(entity_id_iter, constants.SPECIES_COMPONENT) and id_of_self == coordinator.getComponent(entity_id_iter, constants.SPECIES_COMPONENT):
                    other_repo: ReproduceComponent = coordinator.getComponent(entity_id_iter, constants.REPRODUCE_COMPONENT)
                    match reproduce_component.sex:
                        case Sex.MALE:
                            if other_repo.sex != Sex.FEMALE:
                                continue
                        case Sex.FEMALE:
                            if other_repo.sex != Sex.MALE:
                                continue
                        case Sex.OTHER:
                            if other_repo.sex != Sex.OTHER:
                                continue
                    if reproduce_component.others == 1:
                        success = True
                        break
                    elif reproduce_component.others == -1:
                        mod *= 0.5
            if not success:
                continue

        if random.random() > mod:
            continue

        reproduce_component.current += 1

        if reproduce_component.current >= reproduce_component.delay:
            reproduce_component.delay = reproduce_component.cooldown
            count: int = random.randint(0, reproduce_component.count)
            if count == 0: 
                continue
            for _ in range(count):
                pos: Point3D = position + Point3D(random.uniform(-reproduce_component.offset, reproduce_component.offset), random.uniform(-reproduce_component.offset, reproduce_component.offset), 0)
                coordinator.setComponent(terrain.addEntity(coordinator, pos, reproduce_component.species), constants.DIRTY_POSITION_COMPONENT, pos)