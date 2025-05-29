from ..ecs import ECSCoordinator
from ..world.terrain import Terrain
from ..position import Vector3D, Point3D
from ..components.move_to_target_component import MoveToTargetComponent
from ..components.eat_target_component import EatTargetComponent
from ..components.brain_component import BrainComponent
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
            rigid: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)

            if distance.magnitude() > rigid.size:
                direction: Vector3D = distance.asVector3D().norm()
                angle = math.degrees(math.atan2(direction.y, direction.x))
                rigid.rotation = 270 - angle
                coordinator.setComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT, rigid)
                coordinator.setComponent(entity_id, constants.DIRTY_POSITION_COMPONENT, position)
                coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, position + (direction * move_to_target.speed).asPoint3D())

def eatTarget(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.EAT_TARGET_COMPONENT):
        eat_target: EatTargetComponent = coordinator.getComponent(entity_id, constants.EAT_TARGET_COMPONENT)
        physical_body: PhysicalBody = coordinator.getComponent(entity_id, constants.PHYSICAL_BODY_COMPONENT)
        size = physical_body.size
        position: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        if brain_component.target_creature.valid and brain_component.target_creature.creature in coordinator.entities:
            entity_pos: Point3D = coordinator.getComponent(brain_component.target_creature.creature, constants.POSITION_COMPONENT)
            entity_size: Point3D = coordinator.getComponent(brain_component.target_creature.creature, constants.PHYSICAL_BODY_COMPONENT).size
            sizer = entity_size
            if coordinator.hasComponent(brain_component.target_creature.creature, constants.SIZE_HEALTH_COMPONENT):
                health = coordinator.getComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT)
                sizer *= health.current / health.max
            if entity_pos.distSQ(position) <= (sizer + size) ** 2:
                diet: DietComponent = coordinator.getComponent(entity_id, constants.DIET_COMPONENT)
                nutrition: NutrientSource = coordinator.getComponent(brain_component.target_creature.creature, constants.NUTRIENT_SOURCE_COMPONENT)
                #if constants.NutrientType.PROTEIN in nutrition.nutrients:
                    #print(diet)
                    #print(nutrition)
                coordinator.setComponent(entity_id, constants.DIET_COMPONENT, diet.updated(nutrition, eat_target.amount))
                if coordinator.hasComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT):
                    health: HealthComponent = coordinator.getComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT)
                    health.current = min(max(health.current - eat_target.damage, 0), health.max)
                    coordinator.setComponent(brain_component.target_creature.creature, constants.HEALTH_COMPONENT, health)
                elif coordinator.hasComponent(brain_component.target_creature.creature, constants.PHYSICAL_BUZZ):
                    phy: PhysicalBody = coordinator.getComponent(brain_component.target_creature.creature, constants.PHYSICAL_BODY_COMPONENT)
                    phy.size -= eat_target.damage / 360


def brainValidate(coordinator: ECSCoordinator):
    for entity_id in coordinator.getEntitiesWithComponent(constants.BRAIN_COMPONENT):
        brain_component: BrainComponent = coordinator.getComponent(entity_id, constants.BRAIN_COMPONENT)
        to_del = []
        for i, entityer in enumerate(brain_component.entities):
            if entityer.id not in coordinator.entities:
                to_del.append(i)
        
        to_del.reverse()

        for e in to_del:
            brain_component.entities.pop(e)

def epoch(coordinator: ECSCoordinator, terrain: Terrain):
    smergle = set()
    for entity_id in coordinator.getEntitiesWithComponent(constants.POSITION_COMPONENT):
        poiawe: Point3D = coordinator.getComponent(entity_id, constants.POSITION_COMPONENT)
        while poiawe in smergle:
            poiawe += Point3D(random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01), random.uniform(-0.01, 0.01))
        coordinator.setComponent(entity_id, constants.POSITION_COMPONENT, poiawe)
        smergle.add(poiawe)