from ..ecs import ECSCoordinator
from ..position import Point3D
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.eat_target_component import EatTargetComponent
from ..components.brain_component import BrainComponent, Emoticon
from ..components.physical_body import PhysicalBody
from ..components.diet_component import DietComponent
from ..components.nutrient_source import NutrientSource
from ..components.health_component import HealthComponent
from ..components.energy_component import EnergyComponent
from .. import constants
import math, random

def moveToTarget(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.MOVE_TO_TARGET_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_position.valid:
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            distance: Point3D = (brain_component.target_position.position - position).scaleBy(1, 1, 0)
            physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)

            if distance.magnitude() > physical_body.size:
                move_to_target: MoveToTargetComponent = coordinator.getComponent(entity_id, constants.MOVE_TO_TARGET_COMPONENT)
                direction: Point3D = distance.norm()
                angle = math.degrees(math.atan2(direction.y, direction.x))
                physical_body.rotation = 270 - angle
                coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, physical_body)
                coordinator.setComponent(entity_id, constants.DIRTY_POSITION_COMPONENT, position)
                coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + (direction * move_to_target.speed))
                
                energy: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
                energy.current -= max(int(move_to_target.speed), 1)
                coordinator.setComponent(entity_id, constants.ENERGY_COMPONENT, energy)

def eatTarget(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.EAT_TARGET_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_creature.valid and brain_component.target_creature.creature in coordinator.entities:
            physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
            position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
            entity_pos: Point3D = coordinator.getComponent(brain_component.target_creature.creature, constants.POSITION_COMPONENT)
            entity_physical_body: PhysicalBody = coordinator.getComponent(brain_component.target_creature.creature, constants.PHYSICAL_BODY_COMPONENT)
            size_modification = entity_physical_body.size
            if coordinator.hasComponent(brain_component.target_creature.creature, constants.SIZE_HEALTH_COMPONENT):
                health: HealthComponent = coordinator.getComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT)
                size_modification *= health.current / health.max
            if entity_pos.distSQ(position) <= (size_modification + physical_body.size) ** 2:
                eat_target: EatTargetComponent = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT)
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
                    entity_physical_body.size -= eat_target.damage / 360
                energy: EnergyComponent = coordinator.getComponent(entity_id, constants.ENERGY_COMPONENT)
                energy.current -= eat_target.damage
                coordinator.setComponent(entity_id, constants.ENERGY_COMPONENT, energy)


def brainValidate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        brain_component.entities = [entity_instance for entity_instance in brain_component.entities if entity_instance.id in coordinator.entities]

def epoch(coordinator: ECSCoordinator):
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