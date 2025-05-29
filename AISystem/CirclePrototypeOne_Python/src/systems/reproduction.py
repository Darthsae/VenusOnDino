from ..ecs import ECSCoordinator, entity
from ..world.terrain import Terrain
from ..position import Point3D
from ..components.energy_component import EnergyComponent
from ..components.reproduce_component import ReproduceComponent
from ..components.physical_body import PhysicalBody
from ..components.brain_component import BrainComponent, CreatureState
from .. import constants
import random

def updateReproduction(coordinator: ECSCoordinator, terrain: Terrain):
    for entity_id in coordinator.getEntitiesWithComponent(constants.REPRODUCE_COMPONENT):
        reproduce_component: ReproduceComponent = coordinator.getComponent(entity_id, constants.REPRODUCE_COMPONENT)
        if random.random() < reproduce_component.chance:
            if not coordinator.hasComponent(entity_id, constants.ENERGY_COMPONENT):
                reproduce_component.current += 1
            else:
                energy: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
                if energy.current > reproduce_component.energy_use:
                    energy.current -= reproduce_component.energy_use
                    reproduce_component.current += 1
                else:
                    continue

            if coordinator.hasComponent(entity_id, constants.BRAIN_COMPONENT):
                brain: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
                if brain.state != CreatureState.AWAKE:
                    continue
            mod = 1.0
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            if reproduce_component.others != 0:
                physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
                possible: set[tuple[Point3D, entity]] = terrain.entities.query(position - Point3D.fromUniform(physical_body.size * 2), position + Point3D.fromUniform(physical_body.size * 2))
                success: bool = reproduce_component.others != 1
                id_of_self: int = coordinator.getComponent(entity_id, constants.SPECIES_COMPONENT)
                for tup in possible:
                    if tup[1] in coordinator.entities and coordinator.hasComponent(tup[1], constants.SPECIES_COMPONENT) and id_of_self == coordinator.getComponent(tup[1], constants.SPECIES_COMPONENT):
                        if reproduce_component.others == 1:
                            success = True
                            break
                        elif reproduce_component.others == -1:
                            mod *= 0.5
                if not success:
                    continue

            if random.random() < mod:
                if reproduce_component.current >= reproduce_component.delay:
                    reproduce_component.delay = reproduce_component.cooldown
                    for _ in range(random.randint(0, reproduce_component.count)):
                        pos: Point3D = position + Point3D(random.uniform(-reproduce_component.offset, reproduce_component.offset), random.uniform(-reproduce_component.offset, reproduce_component.offset), 0)
                        coordinator.setComponent(terrain.addEntity(coordinator, pos, reproduce_component.species), constants.DIRTY_POSITION_COMPONENT, pos)